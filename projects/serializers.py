from rest_framework import serializers

from .models import Project, Employee
from users.models import Group


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
            raise serializers.ValidationError('Invalid group')
        return group

    def validate(self, data):
        """
        Валидация данных.

        :param data: Данные полученные для валидации.
        :return: Data
        """

        if data['start_time'] > data['end_time']:
            raise serializers.ValidationError("End time must occur after start time")
        return data

class EmployeeSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.name')
    class Meta:
        model = Employee
        fields = ['id', 'name']

class EmployeeIdSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id']
