from rest_framework import generics, permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .projects_permitions import IsEmployeeOfProject, IsEmployeeOfProjectRole, \
    IsEmployee

from projects.models import Project, ProjectRole, Employee
from projects.serializers import ProjectSerializer, ProjectRoleSerializer, \
    EmployeeSerializer, EmployeeUpdateSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    permission_classes = [permissions.IsAuthenticated, IsEmployeeOfProject]
    serializer_class = ProjectSerializer

    def get_serializer(self, *args, **kwargs):
        if self.action == 'add_employees':
            serializer_class = EmployeeSerializer
            kwargs.setdefault('context', self.get_serializer_context())
            return serializer_class(*args, **kwargs)
        return super().get_serializer(*args, **kwargs)

    @action(detail=True, methods=['get', 'post'], url_path='add-employees')
    def add_employees(self, request, pk=None):
        project = self.get_object()

        if not Employee.objects.filter(project=project, user=request.user).exists():
            return Response(
                {
                    'detail': 'Доступ запрещён. '
                              'Вы не являетесь сотрудником этого проекта.'
                },
                status=status.HTTP_403_FORBIDDEN
            )

        if request.method == 'GET':
            group_users = project.group.user_set.all()
            user_data = [
                {
                    'name': user.name,
                    'email': user.email
                }
                for user in group_users
            ]
            return Response(
                {'users': user_data},
                status=status.HTTP_200_OK
            )

        serializer = self.get_serializer(data=request.data)
        serializer.context['project'] = project
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {'detail': 'Сотрудники успешно добавлены'},
            status=status.HTTP_201_CREATED
        )


# class ProjectCreateApiView(generics.CreateAPIView):
#     """
#     CBV, основанное на модели APIView. Отвечает за создание проекта.
#
#     Атрибуты
#     ----------
#     queryset
#         модель для работы с базой данных.
#     serializer_class:
#         класс ответственный за сериализацию/десериализацию данных.
#     permission_classes:
#         регулирование доступа к API.
#     """
#
#     queryset = Project.objects.all()
#     serializer_class = ProjectSerializer
#     permission_classes = (permissions.IsAuthenticated,)

#
# class ProjectDetailApiView(generics.RetrieveUpdateDestroyAPIView):
#     """
#     CBV, совмещающий просмотр, изменение, удаление объекта.
#
#     Атрибуты
#     ----------
#     queryset
#         модель для работы с базой данных.
#     serializer_class:
#         класс ответственный за сериализацию/десериализацию данных.
#     permission_classes:
#         регулирование доступа к API.
#     """
#
#     queryset = Project.objects.all()
#     serializer_class = ProjectSerializer
#     permission_classes = (permissions.IsAuthenticated, ProjectPermissions)


class ProjectRoleViewSet(viewsets.ModelViewSet):
    queryset = ProjectRole.objects.all()
    serializer_class = ProjectRoleSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmployeeOfProjectRole]

class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAuthenticated, IsEmployee]

    def get_serializer(self, *args, **kwargs):
        if self.action == 'update':
            serializer_class = EmployeeUpdateSerializer
            kwargs.setdefault('context', self.get_serializer_context())
            return serializer_class(*args, **kwargs)
        return super().get_serializer(*args, **kwargs)
