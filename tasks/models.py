from django.core.exceptions import ValidationError
from django.db import models
from projects.models import Employee, Project
from users.models import User

class TaskCategory(models.Model):
    """ Категории для классификации задач по темам или типам работ.
        Содержит ключевые слова для автоматической категоризации задач
        с использованием NLP-анализа при создании задач.
        Примеры: 'Разработка', 'Тестирование', 'Документация'
    """
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    keywords = models.TextField(blank=True)

class Status(models.Model):
    TYPE_CHOICES = [
        ('required check', 'Required check'),
        ('planned', 'Planned'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('archived', 'Archived'),
    ]
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, unique=True)
    def save(self, *args, **kwargs):
        valid_statuses = [status[0] for status in self.TYPE_CHOICES]
        if self.type not in valid_statuses:
            raise ValueError(f"Invalid status type: {self.type}. "
                             f"Valid types are {', '.join(valid_statuses)}.")
        super().save(*args, **kwargs)

class Priority(models.Model):
    TYPE_WEIGHT_MAP = {
        'high': 4,
        'medium': 3,
        'low': 2,
        'default': 1
    }
    TYPE_CHOICES = [(key, key.title()) for key in TYPE_WEIGHT_MAP.keys()]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, unique=True)
    def __str__(self):
        return f"{self.get_type_display()} (weight: {self.get_weight()})"
    def get_weight(self):
        return self.TYPE_WEIGHT_MAP[self.type]
    def save(self, *args, **kwargs):
        self.weight = self.TYPE_WEIGHT_MAP[self.type]
        if self.type not in dict(self.TYPE_CHOICES):
            raise ValueError(f"Invalid type: {self.type}. "
                             f"Valid types are {', '.join(dict(self.TYPE_CHOICES).keys())}.")
        super().save(*args, **kwargs)

class Sprint(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("The start date of the sprint must be earlier than the end date.")

class Task(models.Model):
    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("The start date of the task must be earlier than the end date.")
        if self.given_time is not None and self.given_time > self.start_time:
            raise ValidationError("The issue task date cannot be later than the start date.")
    name = models.CharField(max_length=255, null=False)
    description = models.TextField()
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True)
    given_time = models.DateTimeField(null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    priority = models.ForeignKey(Priority, on_delete=models.PROTECT, null=True, blank=True)
    category = models.ForeignKey(
        TaskCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,)
    nlp_metadata = models.JSONField(
        null=True,
        blank=True,
        help_text="Сохраненные результаты NLP анализа (ключевые слова, срочность и т.д.)"
        """
        Метаданные NLP-обработки описания задачи. Содержит:
        - извлеченные ключевые слова
        - распознанные даты/дедлайны
        - оценку срочности
        - другие параметры для автоматического управления задачами
        """
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
