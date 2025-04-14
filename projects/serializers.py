from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from .models import Project, ProjectRole, Employee
from users.models import Group

User = get_user_model()


class ProjectSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Project."""

    class Meta:
        model = Project
        fields = '__all__'

    def validate_group(self, group: Group) -> Group:
        """
        Валидация данных группы.

        :param group: Группа проекта.
        :return: Group
        """

        user_id = self.context['request'].user.id
        if not group.user_set.filter(id=user_id).exists():
            raise serializers.ValidationError('Неверная группа')
        return group

    def validate(self, data):
        """
        Валидация данных.

        :param data: Данные полученные для валидации.
        :return: Data
        """

        if data['start_time'] > data['end_time']:
            raise serializers.ValidationError("Время окончания должно быть"
                                              "после времени начала")
        return data

    def create(self, validated_data) -> Project:
        """
        Создание проекта и дефолтной роли.

        :param validated_data: Обработанные данные.
        :return: Project созданный проект.
        """

        request = self.context.get('request')

        project = Project.objects.create(**validated_data)
        default_role = ProjectRole.objects.create(name="Не указано", project=project)

        Employee.objects.create(
            user=request.user,
            project=project,
            role=default_role
        )
        return project


class ProjectRoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProjectRole
        fields = ['id', 'name', 'project']


class EmployeeSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = Employee
        fields = ['id', 'user', 'user_name', 'project', 'role', 'current_load']
        read_only_fields = ['current_load']

    def create(self, validated_data):
        super().create(validated_data)

        user = validated_data.get('user')
        project = validated_data.get('project')
        role = validated_data.get('role')

        if Employee.objects.filter(user=user).exists():
            raise ValidationError('Такой сотрудник уже существует!')

        if user not in project.group.user_set.all():
            raise ValidationError('Некорректные данные: пользователь, проект')
        if role.project != project:
            raise ValidationError('Некорректная роль.')
        return Employee.objects.create(user=user, project=project, role=role)

class EmployeeUpdateSerializer(EmployeeSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'user', 'user_name', 'project', 'role', 'current_load']
        read_only_fields = ['current_load', 'user']

    def update(self, instance, validated_data):

        user = instance.user
        project = validated_data.get('project')
        role = validated_data.get('role')

        if project.user_set.filter(user=user).exists():
            raise ValidationError('Некорректное значение проекта. '
                                  'Пользователь не находится в группе проекта.')

        if role.project != project:
            raise ValidationError('Некорректная роль.')
        return super().update(instance, validated_data)
