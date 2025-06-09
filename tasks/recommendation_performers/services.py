from projects.models import Project, Employee
from tasks.ml_load_model import load_models
from tasks.ml_utils import get_category_avg_duration
from tasks.models import Task, Executor, Priority, TaskCategory
from tasks.serializers import RecommendationEmployeeSerializer

# http://127.0.0.1:8000/task/recommend/?sprint=8&start_time=2025-06-05T12:05:00&priority=1&description=%D0%BA%D0%B0%D0%BA%D0%BE%D0%B9-%D1%82%D0%BE%D1%82%D0%B5%D0%BA%D1%81%D1%82


def recommend_employees(serializer: RecommendationEmployeeSerializer, top_n=3,
                        weight_time=0.5, weight_load=0.3, weight_shills=0.2):
    serializer_data = serializer.data

    sprint = serializer_data.get('sprint')
    project = Project.objects.get(sprint=sprint)

    candidates = Employee.objects.filter(project=project).all()

    tasks_with_category = Task.objects.filter(
        category=serializer_data.get('category'),
        sprinttask__sprint__project=project
    ).all()
    employee_ids = Executor.objects.filter(
        task__in=tasks_with_category
    ).values_list('employee__user_id', flat=True).distinct()
    candidates_with_experience = candidates.filter(id__in=employee_ids).all()

    scores = []

    models = load_models()
    catboost_model = models.get('catboost')

    for employee in candidates:
        skill_match_score = 1 if employee in candidates_with_experience else 0

        priority_value = Priority.objects.get(id=serializer_data.get('priority'))
        category = TaskCategory.objects.get(id=serializer_data.get('category'))

        priority_weight = priority_value.get_weight() \
            if serializer_data.get('priority') else 0
        category_avg = get_category_avg_duration(category) \
            if category else 0
        description_length = len(serializer_data.get('description')) \
            if serializer_data.get('description') else 0

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

    print([employee for employee, score in scores[:top_n]])

    return [employee.id for employee, score in scores[:top_n]]
