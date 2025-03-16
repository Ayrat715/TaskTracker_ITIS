from django.core.exceptions import ValidationError
from django.db import models
from apps import users, projects


class Status(models.Model):
    # TODO: Посмотрите на типы статусов задач, может будут какие-то предложения еще.
    # TYPE_CHOICES = [
    #     ('active', 'Active'),
    #     ('completed', 'Completed'),
    #     ('archived', 'Archived'),
    # ]
    # type = models.CharField(max_length=20, choices=TYPE_CHOICES, unique=True)
    type = models.CharField(max_length=20, null=False)

# TODO: То же самое, что и со статусами, бек может коррективы какие-то внести.
#  PS: только не делайте миграции пока у себя
# class Priority(models.Model):
#     TYPE_WEIGHT_MAP = {
#         'high': 4,
#         'medium': 3,
#         'low': 2,
#         'default': 1
#     }
#     TYPE_CHOICES = [(key, key.title()) for key in TYPE_WEIGHT_MAP.keys()]
#     type = models.CharField(max_length=10, choices=TYPE_CHOICES, unique=True)
#     weight = models.IntegerField()
#
#     def __str__(self):
#         return f"{self.get_type_display()} (weight: {self.weight})"
#
#     def clean(self):
#         if self.weight != self.TYPE_WEIGHT_MAP.get(self.type):
#             raise ValidationError(
#                 f'Неверный вес для типа {self.type}. '
#                 f'Ожидается {self.TYPE_WEIGHT_MAP[self.type]}'
#             )
#     def save(self, *args, **kwargs):
#         self.weight = self.TYPE_WEIGHT_MAP[self.type]
#         super().save(*args, **kwargs)

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
    # priority = models.ForeignKey(Priority, on_delete=models.PROTECT, default=Priority.objects.get(type='default'))

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
