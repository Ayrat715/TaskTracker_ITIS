from django.db import models


class Group(models.Model):
    name = models.CharField(max_length=13, null=False)

class User(models.Model):  # Бывший Human
    name = models.CharField(max_length=255, null=False)
    email = models.EmailField(unique=True, null=False)
    password = models.CharField(max_length=255, null=False)
    groups = models.ManyToManyField(Group, through='GroupUser')

class GroupUser(models.Model):  # Бывший GroupHuman
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
