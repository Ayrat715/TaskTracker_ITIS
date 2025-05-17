from django.core.exceptions import ValidationError
from model_utils.tracker import FieldTracker
from projects.models import Employee, Project
from tasks.ml_utils import extract_task_features
from users.models import User
import logging
from django.db import models
logger = logging.getLogger(__name__)
import re

class TaskCategory(models.Model):
    """ Категории для классификации задач по темам или типам работ.
        Содержит ключевые слова для автоматической категоризации задач
        с использованием NLP-анализа при создании задач.
        Примеры: 'Разработка', 'Тестирование', 'Документация'
    """
    tracker = FieldTracker(fields=['keywords'])
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    keywords = models.TextField(
        blank=True,
        help_text="Список ключевых слов через запятую"
    )
    processed_keywords = models.TextField(
        blank=True,
        editable=False,
        help_text="Автоматически обработанные ключевые слова"
    )

    def save(self, *args, **kwargs):
        raw_text = self.keywords or ""
        words = [w for w in re.split(r'\W+', raw_text.lower()) if w]
        processed = list(set(words))
        self.processed_keywords = processed
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

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
        if self.type not in dict(self.TYPE_CHOICES):
            raise ValueError(f"Invalid type: {self.type}. "
                             f"Valid types are {', '.join(dict(self.TYPE_CHOICES).keys())}.")
        super().save(*args, **kwargs)


class Sprint(models.Model):
    name = models.CharField()
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("The start date of the sprint must be earlier than the end date.")


class Task(models.Model):
    task_number = models.IntegerField(blank=True, null=True)
    tracker = FieldTracker(fields=['name', 'description'])
    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("The start date of the task must be earlier than the end date.")
        if self.given_time is not None and self.given_time > self.start_time:
            raise ValidationError("The issue task date cannot be later than the start date.")
    name = models.CharField(max_length=255, null=False)
    description = models.TextField(null=True, blank=True)
    status = models.ForeignKey(Status, on_delete=models.SET_NULL, null=True)
    given_time = models.DateTimeField(null=True, blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    author = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    priority = models.ForeignKey(Priority, on_delete=models.PROTECT, null=True, blank=True)
    predicted_duration = models.FloatField(
        null=True,
        blank=True,
        help_text="Предсказанное время выполнения в часах"
    )
    category = models.ForeignKey(
        TaskCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,)
    nlp_metadata = models.JSONField(
        default=dict,
        null=True,
        blank=True,
        help_text="Сохраненные результаты NLP анализа (ключевые слова, срочность и т.д.)"
    )

    def _prepare_prediction_input(self):
        features = extract_task_features(self)
        return features[:-1] # Без времени старта

    # Предсказание длительности задачи
    def predict_duration(self):
        """Возвращает предсказанное время в часах и сохраняет в поле"""
        from tasks.ml_load_model import load_models
        try:
            models = load_models()
            catboost_model = models.get('catboost')
            lstm_model = models.get('lstm')

            if catboost_model is None:
                logger.error("CatBoost модель не загружена")
                return None

            input_data = extract_task_features(self)
            # Используем CatBoost, если статус позволяет
            if self.status and self.status.type == 'planned':
                seconds = catboost_model.predict([input_data])[0]

            else:
                # Иначе LSTM
                if lstm_model is None:
                    logger.error("LSTM модель не загружена")
                    return None

                lstm_input = self._prepare_lstm_input()
                if lstm_input is None:
                    return None
                seconds = lstm_model.predict(lstm_input)[0][0]

            # Переводим секунды в часы, округляем
            hours = round(seconds / 3600, 1)
            self.predicted_duration = hours
            self.save(update_fields=['predicted_duration'])
            return hours

        except Exception as e:
            logger.error(f"Ошибка предсказания: {str(e)}")
            return None

    def _prepare_lstm_input(self):
        completed_tasks = Task.objects.filter(
            status__type='completed',
            start_time__isnull=False
        ).order_by('start_time')

        if not completed_tasks.exists():
            logger.warning("Нет завершенных задач для LSTM")
            return None
        base_time = completed_tasks.first().start_time
        features = extract_task_features(self, base_time)
        return [[features]]

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
    created_at = models.DateTimeField(auto_now_add=True)

def assign_task_number(task):
    sprint_task = task.sprinttask_set.select_related('sprint').first()
    if sprint_task and sprint_task.sprint.project:
        project = sprint_task.sprint.project
        max_number = (
            Task.objects
            .filter(sprinttask__sprint__project=project)
            .exclude(id=task.id)
            .aggregate(models.Max('task_number'))
            .get('task_number__max')
        )
        new_number = (max_number or 0) + 1
    else:
        new_number = 1
    task.task_number = new_number
    task.save(update_fields=["task_number"])
