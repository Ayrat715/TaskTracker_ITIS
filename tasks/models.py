from django.core.exceptions import ValidationError
from django.db import models
from projects.models import Employee, Project
from users.models import User

# TODO: Модель нужна для анализа схожести задач, скорее всего еще в нее поля будем добавлять.
class TaskCategory(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    keywords = models.TextField(blank=True)

# TODO: Модель для статуса задач(какие-то можно еще добавить, это первые, что мне в голову пришли.
class Status(models.Model):
    TYPE_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, unique=True)

# TODO: Тут думаю объяснять ничего не нужно, также жду предложений и коррективов.
class Priority(models.Model):
    TYPE_WEIGHT_MAP = {
        'high': 4,
        'medium': 3,
        'low': 2,
        'default': 1
    }
    TYPE_CHOICES = [(key, key.title()) for key in TYPE_WEIGHT_MAP.keys()]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, unique=True)
    weight = models.IntegerField()

    def __str__(self):
        return f"{self.get_type_display()} (weight: {self.weight})"

    def clean(self):
        if self.weight != self.TYPE_WEIGHT_MAP.get(self.type):
            raise ValidationError(
                f'Неверный вес для типа {self.type}. '
                f'Ожидается {self.TYPE_WEIGHT_MAP[self.type]}'
            )
    def save(self, *args, **kwargs):
        self.weight = self.TYPE_WEIGHT_MAP[self.type]
        super().save(*args, **kwargs)

class Sprint(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

class Task(models.Model):
    name = models.CharField(max_length=255, null=False)
    description = models.TextField()
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True)
    given_time = models.DateTimeField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    priority = models.ForeignKey(Priority, on_delete=models.PROTECT, default=None)
    category = models.ForeignKey(
        TaskCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,)
    nlp_metadata = models.JSONField(
        null=True,
        blank=True,
        help_text="Сохраненные результаты NLP анализа (ключевые слова, срочность и т.д.)"

    )

class Executor(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

class SprintTask(models.Model):
    sprint = models.ForeignKey(Sprint, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

class Comment(models.Model):
    title = models.CharField(max_length=255, null=False)
    body = models.TextField(null=True)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
