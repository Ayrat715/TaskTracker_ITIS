from rest_framework import serializers, status
from rest_framework.response import Response

from projects.models import Employee
from tasks.models import Sprint, Task, SprintTask


class SprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sprint
        fields = '__all__'
        extra_kwargs = {
            'name': {'required': False},
            'description': {'required': False},
            'project': {'required': False}
        }

    def validate(self, data):
        instance = self.instance if self.instance else None
        start_time = data.get('start_time', instance.start_time if instance else None)
        end_time = data.get('end_time', instance.end_time if instance else None)
        if start_time and end_time and start_time > end_time:
            raise serializers.ValidationError("End time must be after start time.")
        return data

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class TaskSerializer(serializers.ModelSerializer):
    executor_id = serializers.PrimaryKeyRelatedField(
        source='executor',
        queryset=Employee.objects.all(),
        write_only=True,
        required=False
    )
    sprint_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True, required=False
    )

    def validate(self, data):
        instance = self.instance if self.instance else None
        start_time = data.get('start_time', instance.start_time if instance else None)
        end_time = data.get('end_time', instance.end_time if instance else None)
        if start_time and end_time and start_time > end_time:
            raise serializers.ValidationError({'non_field_errors':
                                                   ["End time must be after start time."]})
        return data

    class Meta:
        model = Task
        fields = '__all__'
        extra_kwargs = {'executor': {'read_only': True}}

    def create(self, validated_data):
        sprint_ids = validated_data.pop('sprint', [])
        sprints = Sprint.objects.filter(id__in=sprint_ids)
        if len(sprints) != len(sprint_ids):
            return Response({"sprint": ["Some sprints do not exist."]},
                            status=status.HTTP_400_BAD_REQUEST)
        executor = validated_data.pop('executor', None)
        task = Task.objects.create(**validated_data)
        if executor:
            task.executor = executor
            task.save()
        for sprint_id in sprint_ids:
            sprint = Sprint.objects.filter(id=sprint_id).first()
            if sprint:
                SprintTask.objects.create(sprint=sprint, task=task)
        return task

    def update(self, instance, validated_data):
        sprint_ids = validated_data.pop('sprint', None)
        executor = validated_data.pop('executor', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if executor:
            instance.executor = executor
        instance.save()
        if sprint_ids is not None:
            SprintTask.objects.filter(task=instance).delete()
            for sprint_id in sprint_ids:
                sprint = Sprint.objects.filter(id=sprint_id).first()
                if sprint:
                    SprintTask.objects.create(sprint=sprint, task=instance)
        return instance
