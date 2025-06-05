import json

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.http import Http404
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView

from tasks.recommendation_performers.services import recommend_employees
from tasks.serializers import SprintSerializer, TaskSerializer, \
    StatusSerializer, PrioritySerializer, RecommendationEmployeeSerializer
from tasks.models import Sprint, Task, Executor, Priority, Status
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
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error when creating a task: {str(e)}")
            return Response({"error": "An unexpected error occurred."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except Http404:
            return Response({"detail": "Task not found."}, status=404)
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


class EmployeeRecommendation(APIView):
    def get(self, request):
        serializer = RecommendationEmployeeSerializer(data=request.query_params,
                                                      required=True)
        if serializer.is_valid():
            return Response(
                json.dumps(recommend_employees(serializer)),
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
