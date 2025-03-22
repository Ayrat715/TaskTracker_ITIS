from rest_framework import serializers
from projects.models import Employee
from tasks.models import Sprint, Task, SprintTask


class SprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sprint
        fields = '__all__'

    def validate(self, data):
        instance = self.instance if self.instance else None
        start_time = data.get('start_time', instance.start_time if instance else None)
        end_time = data.get('end_time', instance.end_time if instance else None)

        if start_time and end_time and start_time > end_time:
            raise serializers.ValidationError("End time must be after start time.")
        return data

class TaskSerializer(serializers.ModelSerializer):
    executor = serializers.PrimaryKeyRelatedField(queryset=Employee.objects.all())
    sprint_ids = serializers.ListField(child=serializers.IntegerField(),
                                       write_only=True, required=False)

    class Meta:
        model = Task
        fields = '__all__'

    def create(self, validated_data):
        sprint_ids = validated_data.pop('sprint_ids', [])
        task = Task.objects.create(**validated_data)
        for sprint_id in sprint_ids:
            SprintTask.objects.create(sprint_id=sprint_id, task=task)
        return task
