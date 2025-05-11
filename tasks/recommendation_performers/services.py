from projects.models import Project, Employee
from tasks.ml_load_model import load_models
from tasks.ml_utils import get_category_avg_duration
from tasks.models import Task, Executor
from tasks.serializers import RecommendationEmployeeSerializer


def recommend_employees(serializer: RecommendationEmployeeSerializer, top_n=3,
                        weight_time=0.5, weight_load=0.3, weight_shills=0.2):
    serializer_data = serializer.data

    sprint = serializer_data.sprint
    project = Project.objects.get(sprint=sprint)

    candidates = Employee.objects.filter(project=project).all()

    tasks_with_category = Task.objects.filter(
        category=serializer_data.category,
        project=project
    ).all()
    employee_ids = Executor.objects.filter(
        task__in=tasks_with_category
    ).values_list('user_id', flat=True).distinct()
    candidates_with_experience = candidates.filter(id__in=employee_ids).all()

    scores = []

    models = load_models()
    catboost_model = models.get('catboost')

    for employee in candidates:
        skill_match_score = 1 if employee in candidates_with_experience else 0

        priority_weight = serializer_data.priority.get_weight() \
            if serializer_data.priority else 0
        category_avg = get_category_avg_duration(serializer_data.category) \
            if serializer_data.category else 0
        description_length = len(serializer_data.description) \
            if serializer_data.description else 0

        current_load = employee.current_load

        prepared_data = [priority_weight, current_load, category_avg,
                         description_length, 0]

        predicted_time = catboost_model.predict([prepared_data])[0]

        score = (
            predicted_time * weight_time +
            current_load * weight_load +
            (1 - skill_match_score) * weight_shills
        )
        scores.append((employee, score))

    scores.sort(key=lambda x: x[1])

    return [employee for employee, score in scores[:top_n]]
