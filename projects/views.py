from rest_framework import permissions, viewsets, status

from .projects_permitions import IsEmployeeOfProject, IsEmployeeOfProjectRole, \
    IsEmployee

from projects.models import Project, ProjectRole, Employee
from projects.serializers import ProjectSerializer, ProjectRoleSerializer, \
    EmployeeSerializer, EmployeeUpdateSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    permission_classes = (IsEmployeeOfProject, )
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.filter(group__user=self.request.user)


class ProjectRoleViewSet(viewsets.ModelViewSet):
    queryset = ProjectRole.objects.all()
    serializer_class = ProjectRoleSerializer
    permission_classes = [IsEmployeeOfProjectRole]


    def get_queryset(self):
        project_role = ProjectRole.objects.filter(project_id=self.kwargs.get('project_pk'))
        return project_role

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['project_id'] = self.kwargs.get('project_pk')
        return context

    def perform_create(self, serializer):
        serializer.save(project_id=self.kwargs.get('project_pk'))


class EmployeeViewSet(viewsets.ModelViewSet):
    serializer_class = EmployeeSerializer
    permission_classes = [IsEmployee]

    def get_queryset(self):
        return Employee.objects.filter(project__id = self.kwargs.get('project_pk'))

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['project_id'] = self.kwargs.get('project_pk')
        return context

    def perform_create(self, serializer):
        serializer.save(project_id=self.kwargs.get('project_pk'))

    def get_serializer(self, *args, **kwargs):
        if self.action == 'update':
            serializer_class = EmployeeUpdateSerializer
            kwargs.setdefault('context', self.get_serializer_context())
            return serializer_class(*args, **kwargs)
        return super().get_serializer(*args, **kwargs)
