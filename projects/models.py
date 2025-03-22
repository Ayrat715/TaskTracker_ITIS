from django.db import models
from users.models import User, Group


class Project(models.Model):
    name = models.CharField(max_length=50, null=False)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

class ProjectRole(models.Model):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

class Employee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role = models.ForeignKey(ProjectRole, on_delete=models.SET_NULL, null=True)
    current_load = models.IntegerField(default=0)
    @property
    def completed_tasks_count(self):
        return self.executor_set.filter(task__status__type='completed').count()

    @property
    def average_completion_time(self):
        completed_tasks = self.executor_set.filter(task__status__type='completed')
        total = sum((t.task.end_time - t.task.start_time).total_seconds() for t in completed_tasks)
        return total / len(completed_tasks) if completed_tasks else 0
