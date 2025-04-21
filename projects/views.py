from django.db.models import QuerySet
from rest_framework import generics, permissions
from rest_framework.response import Response
from .projects_permitions import ProjectPermissions
from projects.models import Project, Employee
from projects.serializers import ProjectSerializer, EmployeeSerializer, EmployeeIdSerializer


class ProjectCreateApiView(generics.CreateAPIView):
    """
    CBV, основанное на модели APIView. Отвечает за создание проекта.

    Атрибуты
    ----------
    queryset
        модель для работы с базой данных.
    serializer_class:
        класс ответственный за сериализацию/десериализацию данных.
    permission_classes:
        регулирование доступа к API.
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (permissions.IsAuthenticated,)


class ProjectDetailApiView(generics.RetrieveUpdateDestroyAPIView):
    """
    CBV, совмещающий просмотр, изменение, удаление объекта.

    Атрибуты
    ----------
    queryset
        модель для работы с базой данных.
    serializer_class:
        класс ответственный за сериализацию/десериализацию данных.
    permission_classes:
        регулирование доступа к API.
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = (permissions.IsAuthenticated, ProjectPermissions)

class UserProjectListViewSet(generics.ListAPIView):
    """
    Список проектов авторизованного пользователя.

    Атрибуты
    ----------
    model:
        Экземпляр модели
    serializer_class:
        Класс, реализующий сериализацию.
    permission_classes:
        Класс, регулирующий доступ к ресурсу.
    """

    model = Project
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self) -> QuerySet:
        """
        Получение экземпляра проектов по авторизованному пользователю.

        :return: QuerySet список проектов, принадлежащих авторизованному
        пользователю.
        """

        user_id = self.request.user.id
        return Project.objects.filter(group__user=user_id)


class ProjectEmployeesView(generics.ListAPIView):
    serializer_class = EmployeeSerializer
    def get_queryset(self):
        project_id = self.kwargs.get('project_id')
        return Employee.objects.filter(project_id=project_id)


class MyEmployeeIdView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = EmployeeIdSerializer

    def get_queryset(self):
        # Возвращаем только ID сотрудников текущего пользователя
        return Employee.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        # Получаем queryset, как обычно
        queryset = self.get_queryset()
        # Создаем список ID сотрудников текущего пользователя
        employee_ids = list(queryset.values_list('id', flat=True))
        # Формируем ответ в нужном формате
        return Response({"id": employee_ids})

