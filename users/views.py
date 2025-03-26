from http import HTTPStatus

from django.contrib.auth import login
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.serializers import UserRegistrationSerializer, UserLoginSerializer


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

    def post(self, request):
        """

        :param request: информация о запросе
        :returns: Response: ошибка 400 при некорректных данных / статус 200,
        когда аутентификация была выполнена успешно
        """

        serializer = UserLoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.validated_data['user']
        login(request, user)
        return Response(HTTPStatus.OK)
