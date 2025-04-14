from rest_framework import serializers
from projects.models import Employee
from tasks.models import Sprint, Task, SprintTask, Status, Priority


class StatusSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(source='get_type_display')

    class Meta:
        model = Status
        fields = ['type', 'display_name']

class PrioritySerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(source='get_type_display')
    weight = serializers.IntegerField(source='get_weight')

    class Meta:
        model = Priority
        fields = ['type', 'display_name', 'weight']

class SprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sprint
        fields = '__all__'
        extra_kwargs = {
            'description': {'required': False}
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
        write_only=True,
        required=False
    )

    class Meta:
        model = Task
        fields = '__all__'
        extra_kwargs = {
            'predicted_duration': {'read_only': True},
            'category': {'read_only': True},
            'nlp_metadata': {'read_only': True},
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('category', None)
        representation.pop('nlp_metadata', None)
        return representation

    def validate(self, data):
        instance = self.instance if self.instance else None

        start_time = data.get('start_time', instance.start_time if instance else None)
        end_time = data.get('end_time', instance.end_time if instance else None)

        if start_time and end_time and start_time > end_time:
            raise serializers.ValidationError({'non_field_errors': ["End time must be after start time."]})

        sprint_ids = data.get('sprint_ids', [])
        executor = data.get('executor', None)

        if sprint_ids and executor:
            sprints = Sprint.objects.filter(id__in=sprint_ids)
            projects = set(sprint.project_id for sprint in sprints)

            if len(projects) > 1:
                raise serializers.ValidationError({'sprint_ids': ["All sprints must belong to the same project."]})

            project_id = next(iter(projects))
            if executor.project_id != project_id:
                raise serializers.ValidationError({'executor_id': ["Executor does not belong to the project's team."]})

        return data

    def create(self, validated_data):
        sprint_ids = validated_data.pop('sprint_ids', [])
        sprints = Sprint.objects.filter(id__in=sprint_ids)
        if len(sprints) != len(sprint_ids):
            raise serializers.ValidationError({"sprint_ids": ["Some sprints do not exist."]})

        executor = validated_data.pop('executor', None)
        task = Task.objects.create(**validated_data)
        if executor:
            task.executor = executor
            task.save()
        for sprint in sprints:
            SprintTask.objects.create(sprint=sprint, task=task)
        return task

    def update(self, instance, validated_data):
        if 'start_time' in validated_data:
            validated_data.pop('start_time')
        sprint_ids = validated_data.pop('sprint_ids', None)
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
        instance.tracker.changed()
        return instance

