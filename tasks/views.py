from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.http import Http404
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from projects.models import Employee
from tasks.serializers import SprintSerializer, TaskSerializer, StatusSerializer, PrioritySerializer
from tasks.models import Sprint, Task, SprintTask, Executor, Priority, Status
import logging
logger = logging.getLogger(__name__)

class StatusListView(APIView):
    def get(self, request):
        statuses = Status.objects.all().order_by('id')
        serializer = StatusSerializer(statuses, many=True)
        return Response(serializer.data)

class PriorityListView(APIView):
    def get(self, request):
        priorities = Priority.objects.all().order_by('id')
        serializer = PrioritySerializer(priorities, many=True)
        return Response(serializer.data)
class SprintViewSet(viewsets.ModelViewSet):
    queryset = Sprint.objects.all()
    serializer_class = SprintSerializer
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return super().create(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error when creating a sprint: {str(e)}")
            return Response({"error": "Server Error"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=kwargs.pop('partial', False))
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

    def create(self, request, *args, **kwargs):
        try:
            sprint_ids = request.data.get('sprint', [])
            sprints = Sprint.objects.filter(id__in=sprint_ids)
            if len(sprints) != len(sprint_ids):
                return Response({"sprint": ["Some sprints do not exist."]},
                                status=status.HTTP_400_BAD_REQUEST)
            employee_id = request.data.get('executor_id')
            if not employee_id:
                return Response({"executor_id": ["This field is required."]}, status=400)
            executor = get_object_or_404(Employee, id=employee_id)
            project_ids = sprints.values_list('project_id', flat=True)
            if executor.project_id not in project_ids:
                return Response(
                    {"executor": ["The executor does not belong to any of the selected sprints' projects."]},
                    status=status.HTTP_400_BAD_REQUEST)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            task = serializer.save()
            Executor.objects.create(task=task, employee=executor)
            for sprint in sprints:
                SprintTask.objects.create(sprint=sprint, task=task)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Http404:
            logger.error("Employee not found")
            return Response({"executor_id": ["Employee not found."]}, status=400)
        except Exception as e:
            logger.error(f"Error when creating a task: {str(e)}")
            return Response({"error": "An unexpected error occurred."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            sprint_ids = request.data.get('sprint', [])
            sprints = Sprint.objects.filter(id__in=sprint_ids)
            if len(sprints) != len(sprint_ids):
                return Response({"sprint": ["Some sprints do not exist."]}, status=400)
            if 'executor_id' in request.data:
                executor = get_object_or_404(Employee, id=request.data['executor_id'])
                project_ids = sprints.values_list('project_id', flat=True)
                if executor.project_id not in project_ids:
                    return Response({"executor_id": ["Executor does not belong to the project."]},
                                    status=400)
                instance.executor = executor
            instance.sprinttask_set.all().delete()
            for sprint in sprints:
                SprintTask.objects.create(sprint=sprint, task=instance)
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            try:
                serializer.is_valid(raise_exception=True)
            except ValidationError as e:
                return Response(e.detail, status=400)
            serializer.save()
            return Response(serializer.data)
        except Http404:
            return Response({"executor_id": ["Employee not found."]}, status=400)
        except Exception as e:
            logger.error(f"Error updating task: {str(e)}")
            return Response({"error": "Server Error"}, status=500)

# Сигнал для обновления нагрузки сотрудника при изменениях в назначениях
@receiver([post_save, post_delete], sender=Executor)
def update_employee_load(sender, instance, **kwargs):
    """Обновляет текущую нагрузку сотрудника на основе активных задач"""
    employee = instance.employee
    # Получаем все активные задачи сотрудника
    active_tasks = employee.executor_set.filter(task__status__type='active')
    # Рассчитываем общую нагрузку как количество активных задач
    total_load = active_tasks.count()
    # Обновляем и сохраняем нагрузку сотрудника
    employee.current_load = total_load
    employee.save(update_fields=['current_load'])
