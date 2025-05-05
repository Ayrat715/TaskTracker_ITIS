from http import HTTPStatus

from django.contrib.auth import login, get_user_model
from django.contrib.auth.models import Group
from django.db.models import QuerySet
from django.http import Http404
from django.shortcuts import get_list_or_404
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import (UserRegistrationSerializer, UserLoginSerializer,
                               UserSerializer, GroupCreateSerializer,
                               GroupUpdateSerializer, User, UserDataSerializer)
from users.users_permitions import UserPermitions


# Create your views here.

class UserRegistrationView(generics.CreateAPIView):
    """
    API view для регистрации пользователей.

    Атрибуты
    ----------
    serializer_class используемый сериализатор для обработки входных данных.
    permission_classes предоставляет доступ всем пользователям, в том числе
    неавторизованным
    """

    serializer_class = UserRegistrationSerializer
    permission_classes = (permissions.AllowAny,)


class UserLoginView(APIView):
    """
    API view для аутентификации пользователя.

    Атрибуты
    ----------
    permission_classes предоставляет доступ всем пользователям, в том числе
    неавторизованным
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request) -> Response:
        """

        :param request: информация о запросе
        :returns: Response: ошибка 400 при некорректных данных / статус 200,
        когда аутентификация была выполнена успешно
        """

        serializer = UserLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        user = serializer.validated_data['user']
        login(request, user)
        data = UserDataSerializer(user).data
        return Response(
            {
                "message": "Login successful",
                "user-data": data
            },
            HTTPStatus.OK)


class UserListView(generics.ListAPIView):
    """
    CBV, ответственный за работу поисковой
    системы пользователей по электронной почте.

    Атрибуты
    ----------
    serializer_class
        класс для сериализации данных.

    permission_classes
        регулирование доступа к API.
    """

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Получение отфильтрованного queryset user'а по полю email.

        :return: List: список пользователей, у которых почта содержит значение
        email из параметра GET запроса.
        """

        users = get_list_or_404(get_user_model(),
                                email__contains=self.request.GET.get('email'))
        return users

    def list(self, request, *args, **kwargs):
        """
        Регулирование способа сериализации данных: множественная сериализация.

        :return: Response: ответ, содержащий пользователей, удовлетворяющих
        условию фильтрации.
        """

        queryset = self.get_queryset()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)


class GroupViewSet(viewsets.ViewSet):
    """
    ViewSet, реализующий работу с группой

    Атрибуты
    ----------
    model
        класс - объект.

    permission_classes
        классы, регламентирующие доступ к ресурсу.
    """

    model = Group
    permission_classes = [IsAuthenticated, UserPermitions]

    def get_object(self, pk: int) -> Response | Group:
        """
        Получение группы по id primary key и проверка доступа к объекту.

        :param pk: id
        :return: Response|Group
        """

        try:
            group = Group.objects.get(pk=pk)
        except Group.DoesNotExist:
            return Response(
                {
                    'error': 'Группа не найдена.'
                },
                status=status.HTTP_404_NOT_FOUND
            )
        self.check_object_permissions(self.request, group)
        return group

    def list(self, request) -> Response:
        """
        Формирование списка групп.

        :param request: данные запроса.
        :return: Response ответ в формате id: int, name: str, users: list.
        """

        groups = Group.objects.all()
        data = [
            {
                'id': group.id,
                'name': group.name,
                'users': list(group.user_set.values_list('id', flat=True))
            }
            for group in groups
        ]
        return Response(data)

    def create(self, request) -> Response:
        """
        Создание группы.

        :param request: данные запроса.
        :return: Response данные о группе в формате id: int, name: str.
        """

        serializer = GroupCreateSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        group = serializer.save()
        return Response(
            {
                'id': group.id,
                'name': group.name
            },
            status=status.HTTP_201_CREATED
        )

    def update(self, request, pk=None) -> Response:
        """
        Изменение данных о группе: состав группы.
        По переданному id пользователя осуществляется добавление в группу.

        :param request: данные запроса.
        :param pk: id пользователя - первичный ключ
        :return: Response информация о группе в формате id: int, name: str.
        """

        group = self.get_object(pk)
        serializer = GroupUpdateSerializer(group, data=request.data,
                                           partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                'id': group.id,
                'name': group.name,
            }
        )

    @action(detail=True, methods=['delete'],
            url_path='remove-user/(?P<user_id>[^/.]+)')
    def remove_user(self, request, pk=None, user_id=None) -> Response:
        """
        Удаление пользователя из группы по дополнительному URL адресу
        "/remove-user/{user_id}".

        :param request: данные запроса.
        :param pk: id группы - primary key
        :param user_id: id пользователя
        :return: Response данные о состоянии пользователя внутри группы:
        1. detail - информация об удалении пользователя,
        2. error - сообщение о том, что указанный пользователь не был найден.
        """

        group = self.get_object(pk)
        try:
            user = get_user_model().objects.get(pk=user_id)
            user.groups.remove(group)
            return Response(
                {
                    'detail': 'Пользователь удалён из группы.'
                }
            )
        except User.DoesNotExist:
            return Response(
                {
                    'error': 'Пользователь не найден.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

    def destroy(self, request, pk=None) -> Response:
        """
        Удаление группы.

        :param request: данные запроса.
        :param pk: id группы - primary key
        :return: Response статус код удаления контента (204)
        """

        group = self.get_object(pk)
        group.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class Logout(APIView):
    """
    Осуществление выхода из аккаунта.

    Атрибуты
    ----------
    permission_classes:
        Классы, регулирующие доступ к endpoint.
    """

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request) -> Response:
        """
        Выполнение выхода из аккаунта через GET метод.

        :param request: Данные запроса.
        :return: Response ответ на запрос 200 - при успешном выходе.
        """

        request.user.auth_token.delete()
        return Response(status=status.HTTP_200_OK)


class UserStatus(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self) -> User:
        if self.request.user.is_authenticated:
            return User.objects.get(id=self.request.user.id)
