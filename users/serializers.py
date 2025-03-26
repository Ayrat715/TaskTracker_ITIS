from django.contrib.auth import get_user_model, authenticate, \
    password_validation
from django.contrib.auth.hashers import make_password
from rest_framework import serializers

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации пользователя.

    Атрибуты
    ----------
    password2 дополнительное поле к модели User для подтверждения пароля
    """

    password2 = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    class Meta:
        model = User
        fields = ['name', 'email', 'password', 'password2']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        """
        Проверяет:
        1. Совпадение паролей
        2. Соответствие пароля стандартным требованиям безопасности Django.
        :param data: данные для обработки
        :return: корректные данные
        """

        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password:": "Passwords do not match"})
        password_validation.validate_password(data['password'])
        return data

    def create(self, validated_data):
        """
        Создание нового пользователя.

        :param validated_data: корректные данные
        :return: нового пользователя
        """

        validated_data.pop('password2')
        validated_data['password'] = make_password(validated_data['password'])
        user = User.objects.create(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Сериализатор для входа в систему.

    Атрибуты
    ----------
    email поле для ввода почты
    password текстовое поле с типом ввода - пароль
    """

    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    def validate(self, data):
        """
        Аутентификация пользователя и проверка данных учётной записи.

        :param data: данные для обработки
        :return: пользователя
        """

        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError({"email:": "Email or password is incorrect"})
        return {'user': user}
