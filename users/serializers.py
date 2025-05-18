import uuid

from django.contrib.auth import get_user_model, authenticate, \
    password_validation
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from rest_framework import serializers

User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для регистрации пользователя.

    Атрибуты
    ----------
    password2
        Дополнительное поле к модели User для подтверждения пароля
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
        :param data: Данные для обработки
        :return: Корректные данные
        """

        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password:": "Passwords do not match"})
        password_validation.validate_password(data['password'])
        return data

    def create(self, validated_data):
        """
        Создание нового пользователя.

        :param validated_data: Корректные данные
        :return: Нового пользователя
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
    email
        Поле для ввода почты
    password
        Текстовое поле с типом ввода - пароль
    """

    email = serializers.EmailField()
    password = serializers.CharField(style={'input_type': 'password'}, write_only=True)

    def validate(self, data):
        """
        Аутентификация пользователя и проверка данных учётной записи.

        :param data: Данные для обработки
        :return: пользователя
        """

        user = authenticate(email=data['email'], password=data['password'])
        if not user:
            raise serializers.ValidationError({"email:": "Email or password is incorrect"})
        return {'user': user}


class UserSerializer(serializers.ModelSerializer):
    """Сериализация данных отображения пользователя."""

    class Meta:
        model = User
        fields = ['id', 'email']


class UserDataSerializer(serializers.ModelSerializer):
    """Информация о пользователе."""

    class Meta:
        model = User
        exclude = ['password']


class GroupCreateSerializer(serializers.ModelSerializer):
    """
    Работа с данными при создании группы.

    Атрибуты
    ----------
    users
        Целочисленный список id пользователей
    """

    users = serializers.ListField(
        child=serializers.IntegerField(), write_only=True
    )

    class Meta:
        model = Group
        fields = ['users']

    def validate_users(self, value) -> QuerySet:
        """
        Валидация данных в поле users.

        :param value: Значение поля users.
        :return: QuerySet список пользователей.
        """

        users = get_user_model().objects.filter(id__in=value)

        if self.context.get('request').user.id not in users:
            user_model = get_user_model()
            user_id = self.context.get('request').user.pk
            request_user_queryset = user_model.objects.filter(
                pk=user_id
            )

            users = users.union(request_user_queryset)
            value.append(user_id)

        if len(users) != len(set(value)):
            raise serializers.ValidationError("Некоторые пользователи "
                                              "не найдены")
        return users

    def create(self, validated_data: dict) -> Group:
        """
        Создание группы.

        :param validated_data: Валидные данные.
        :return: Group экземпляр модели группа.
        """

        name_group = uuid.uuid4()
        while Group.objects.filter(name=name_group).exists():
            name_group = uuid.uuid4()
        group = Group(name=str(name_group))
        group.save()

        users = validated_data.pop('users')
        for user in users:
            user.groups.add(group)
        return group


class GroupUpdateSerializer(serializers.ModelSerializer):
    """
    Обработка данных изменения группы.

    Атрибуты
    ----------
    add_user_id
        Целое число - id пользователя.
    """

    add_user_id = serializers.IntegerField(required=False)

    class Meta:
        model = Group
        fields = ['id', 'add_user_id']

    def update(self, instance: set, validated_data: dict) -> dict:
        """
        Изменение данных группы.

        :param instance: Экземпляр группы.
        :param validated_data: Валидные данные.
        :return: dict группа.
        """

        user_id = validated_data.pop('add_user_id', None)
        if user_id:
            user = get_object_or_404(get_user_model(), id=user_id)
            user.groups.add(instance)
        return instance


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['id', 'name']
        read_only_fields = ['id']


class UserDetailSerializer(UserSerializer):
    groups = GroupSerializer(many=True, read_only=True)

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ['name', 'groups']
