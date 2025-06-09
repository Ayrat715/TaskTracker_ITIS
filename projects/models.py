from django.db import models
from rest_framework.exceptions import ValidationError
from users.models import User, Group


class Project(models.Model):
    name = models.CharField(max_length=50, null=False)
    description = models.TextField(null=True)
    start_time = models.DateTimeField(null=False)
    end_time = models.DateTimeField(null=True)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def clean(self):
        if self.end_time is not None and self.start_time >= self.end_time:
            raise ValidationError("End time must be after start time.")

class ProjectRole(models.Model):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

class Employee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.ForeignKey(ProjectRole, on_delete=models.SET_NULL, null=True)
    current_load = models.IntegerField(default=0)
    """
    Текущая нагрузка сотрудника в условных единицах.
    Используется для балансировки распределения задач между сотрудниками.
    Может рассчитываться на основе количества активных задач и их сложности.
    """
    @property
    def completed_tasks_count(self):
        return self.executor_set.filter(task__status__type='completed').count()
    """
    Количество завершенных задач сотрудника.
    Используется в расчетах KPI и статистики проекта.
    """
    @property
    def average_completion_time(self):
        completed_tasks = self.executor_set.filter(task__status__type='completed')
        total = sum((t.task.end_time - t.task.start_time).total_seconds() for t in completed_tasks)
        return total / len(completed_tasks) if completed_tasks else 0
    """
    Среднее время выполнения задач сотрудником.
    Рассчитывается как отношение общего времени выполнения 
    всех завершенных задач к их количеству.
    Помогает оценивать эффективность и планировать сроки.
    """
