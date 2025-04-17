from rest_framework import serializers
from projects.models import Employee
from tasks.models import Sprint, Task, SprintTask, Status, Priority, Executor


class StatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Status
        fields = ['id', 'type']

class PrioritySerializer(serializers.ModelSerializer):
    weight = serializers.IntegerField(source='get_weight')
    class Meta:
        model = Priority
        fields = ['id', 'type', 'weight']

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
    executor_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        allow_empty=True,
        max_length=5
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
        representation['executors'] = list(instance.executor_set.values_list('employee_id', flat=True))
        representation['sprints'] = list(instance.sprinttask_set.values_list('sprint_id', flat=True))
        return representation

    def validate(self, data):
        instance = self.instance if self.instance else None

        start_time = data.get('start_time', instance.start_time if instance else None)
        end_time = data.get('end_time', instance.end_time if instance else None)

        if start_time and end_time and start_time > end_time:
            raise serializers.ValidationError({'non_field_errors': ["End time must be after start time."]})

        sprint_ids = data.get('sprint_ids', [])
        executor_ids = data.get('executor_ids', [])

        if len(set(executor_ids)) > 5:
            raise serializers.ValidationError({'executor_ids': ["No more than 5 executors are allowed."]})

        if sprint_ids and executor_ids:
            sprints = Sprint.objects.filter(id__in=sprint_ids)
            projects = set(sprint.project_id for sprint in sprints)

            if len(projects) > 1:
                raise serializers.ValidationError({'sprint_ids': ["All sprints must belong to the same project."]})

            project_id = next(iter(projects))
            employees = Employee.objects.filter(id__in=executor_ids)
            for emp in employees:
                if emp.project_id != project_id:
                    raise serializers.ValidationError({'executor_ids': [f"Employee {emp.id} does not belong to the project."]})

        return data

    def create(self, validated_data):
        sprint_ids = validated_data.pop('sprint_ids', [])
        executor_ids = validated_data.pop('executor_ids', [])

        sprints = Sprint.objects.filter(id__in=sprint_ids)
        if len(sprints) != len(sprint_ids):
            raise serializers.ValidationError({"sprint_ids": ["Some sprints do not exist."]})

        executors = Employee.objects.filter(id__in=executor_ids)
        if len(executors) != len(executor_ids):
            raise serializers.ValidationError({"executor_ids": ["Some executors do not exist."]})

        task = Task.objects.create(**validated_data)

        for emp in executors:
            Executor.objects.create(task=task, employee=emp)

        for sprint in sprints:
            SprintTask.objects.create(sprint=sprint, task=task)

        return task

    def update(self, instance, validated_data):
        validated_data.pop('start_time', None)

        sprint_ids = validated_data.pop('sprint_ids', None)
        executor_ids = validated_data.pop('executor_ids', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if executor_ids is not None:
            Executor.objects.filter(task=instance).delete()
            executors = Employee.objects.filter(id__in=executor_ids)
            for emp in executors:
                Executor.objects.create(task=instance, employee=emp)

        if sprint_ids is not None:
            SprintTask.objects.filter(task=instance).delete()
            for sprint_id in sprint_ids:
                sprint = Sprint.objects.filter(id=sprint_id).first()
                if sprint:
                    SprintTask.objects.create(sprint=sprint, task=instance)

        instance.tracker.changed()
        return instance

