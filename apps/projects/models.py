from django.db import models
from apps import users


class Project(models.Model):
    name = models.CharField(max_length=50, null=False)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    group = models.ForeignKey('users.Group', on_delete=models.CASCADE)

class ProjectRole(models.Model):
    name = models.CharField(max_length=255)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

class Employee(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    role_id = models.ForeignKey(ProjectRole, on_delete=models.SET_NULL, null=True)
