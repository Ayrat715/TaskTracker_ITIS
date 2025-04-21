from rest_framework import serializers
from projects.models import Employee
from tasks.models import Sprint, Task, Status, Priority, Executor, assign_task_number
from tasks.models import SprintTask

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
            if len(sprints) != len(sprint_ids):
                raise serializers.ValidationError({'sprint_ids': ["Some sprint IDs are invalid."]})

            projects = {sprint.project_id for sprint in sprints}
            if len(projects) > 1:
                raise serializers.ValidationError({'sprint_ids': ["All sprints must belong to the same project."]})

            project_id = next(iter(projects))
            employees = Employee.objects.filter(id__in=executor_ids)
            if len(employees) != len(executor_ids):
                raise serializers.ValidationError({'executor_ids': ["Some employee IDs are invalid."]})

            for emp in employees:
                if emp.project_id != project_id:
                    raise serializers.ValidationError({'executor_ids': [f"Employee {emp.id} does not belong to the project."]})

        return data

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('category', None)
        representation.pop('nlp_metadata', None)

        representation['executor_ids'] = list(
            instance.executor_set.values_list('employee_id', flat=True)
        )
        representation['sprint_ids'] = list(
            SprintTask.objects.filter(task=instance).values_list('sprint_id', flat=True)
        )
        return representation

    def create(self, validated_data):
        sprint_ids = validated_data.pop('sprint_ids', [])
        executor_ids = validated_data.pop('executor_ids', [])
        task = super().create(validated_data)
        if executor_ids:
            employees = Employee.objects.filter(id__in=executor_ids)
            Executor.objects.bulk_create([
                Executor(task=task, employee=emp) for emp in employees
            ])

        if sprint_ids:
            sprints = Sprint.objects.filter(id__in=sprint_ids)
            SprintTask.objects.bulk_create([
                SprintTask(task=task, sprint=sprint) for sprint in sprints
            ])
        task.refresh_from_db()
        assign_task_number(task)
        return task

    def update(self, instance, validated_data):
        sprint_ids = validated_data.pop('sprint_ids', None)
        executor_ids = validated_data.pop('executor_ids', None)

        task = super().update(instance, validated_data)

        if sprint_ids is not None:
            SprintTask.objects.filter(task=task).delete()
            if sprint_ids:
                sprints = Sprint.objects.filter(id__in=sprint_ids)
                if len(sprints) != len(sprint_ids):
                    raise serializers.ValidationError({"sprint_ids": ["Some sprints are invalid."]})
                SprintTask.objects.bulk_create([
                    SprintTask(task=task, sprint=sprint) for sprint in sprints
                ])

        if executor_ids is not None:
            Executor.objects.filter(task=task).delete()
            if executor_ids:
                employees = Employee.objects.filter(id__in=executor_ids)
                if len(employees) != len(executor_ids):
                    raise serializers.ValidationError({"executor_ids": ["Some employees are invalid."]})
                Executor.objects.bulk_create([
                    Executor(task=task, employee=emp) for emp in employees
                ])

        return task
