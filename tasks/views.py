from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from projects.models import Employee
from tasks.serializers import SprintSerializer, TaskSerializer
from tasks.models import Sprint, Task, SprintTask, Executor
import logging
logger = logging.getLogger(__name__)


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
            employee_id = request.data.get('executor')
            executor = get_object_or_404(Employee, id=employee_id)
            project_ids = sprints.values_list('project_id', flat=True)
            if executor.project_id not in project_ids:
                return Response(
                    {"executor": ["The executor does not belong to any of "
                                  "the selected sprints' projects."]},
                    status=status.HTTP_400_BAD_REQUEST)
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            task = serializer.save()
            Executor.objects.create(task=task, employee=executor)
            for sprint in sprints:
                SprintTask.objects.create(sprint=sprint, task=task)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
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
            if 'executor' in request.data:
                executor = get_object_or_404(Employee, id=request.data['executor'])
                project_ids = sprints.values_list('project_id', flat=True)
                if executor.project_id not in project_ids:
                    return Response({"executor": ["Executor does not belong to the project."]},
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
        except Exception as e:
            logger.error(f"Error updating task: {str(e)}")
            return Response({"error": "Server Error"}, status=500)
