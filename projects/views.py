from rest_framework import generics, permissions

from .projects_permitions import ProjectPermissions

from projects.models import Project
from projects.serializers import ProjectSerializer


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
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


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
