from django.db import models
from apps import users, projects


class Status(models.Model):
    type = models.CharField(max_length=20, null=False)

class Sprint(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)

class Task(models.Model):
    name = models.CharField(max_length=255, null=False)
    description = models.TextField()
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True)
    given_time = models.DateTimeField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    author = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True)

class Executor(models.Model):
    employee = models.ForeignKey('projects.Employee', on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

class SprintTask(models.Model):
    sprint = models.ForeignKey(Sprint, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

class Comment(models.Model):
    title = models.CharField(max_length=255, null=False)
    body = models.TextField(null=True)
    employee = models.ForeignKey('projects.Employee', on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
