from django.core.exceptions import ValidationError
from django.db import models
from model_utils.tracker import FieldTracker
from projects.models import Employee, Project
from tasks.text_processing import preprocess
from tasks.ml_utils import extract_task_features
from users.models import User
import logging
logger = logging.getLogger(__name__)

class TaskCategory(models.Model):
    """ Категории для классификации задач по темам или типам работ.
        Содержит ключевые слова для автоматической категоризации задач
        с использованием NLP-анализа при создании задач.
        Примеры: 'Разработка', 'Тестирование', 'Документация'
    """
    # Отслеживание изменений определённых полей
    tracker = FieldTracker(fields=['keywords', 'auto_assign', 'min_confidence'])
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
        if self.keywords:
            print(f"Processing keywords: {self.keywords}")
            processed = []
            for kw in self.keywords.split(','):
                cleaned_kw = kw.strip()
                if cleaned_kw:
                    try:
                        # Обработка ключевого слова (лемматизация, нормализация и т.п.)
                        processed_kw = preprocess(cleaned_kw)
                        processed.append(processed_kw)
                    except Exception as e:
                        print(f"Error processing '{cleaned_kw}': {str(e)}")
                        continue  # Пропуск некорректные ключи
            self.processed_keywords = ','.join(processed)
            print(f"Processed keywords: {self.processed_keywords}")
        super().save(*args, **kwargs)
    # Определяет, нужно ли автоматически присваивать категорию при создании задачи
    auto_assign = models.BooleanField(default=False)
    # Минимальная уверенность для автоматической классификации
    min_confidence = models.FloatField(default=0.7)


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
    name = models.CharField(max_length=50)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def clean(self):
        if self.start_time >= self.end_time:
            raise ValidationError("The start date of the sprint must be earlier than the end date.")


class Task(models.Model):
    tracker = FieldTracker(fields=['name', 'description'])
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

    # Формирует входные признаки (features) для моделей машинного обучения, исключая время
    def _prepare_prediction_input(self):
        features = extract_task_features(self)
        return features[:-1] # Без времени старта

    # Предсказание длительности задачи с помощью XGBoost или LSTM
    def predict_duration(self):
        """Возвращает предсказанное время в часах и сохраняет в поле"""
        from tasks.ml_utils import should_use_xgb
        from tasks.ml_load_model import load_models
        import joblib
        from django.conf import settings
        import os

        try:
            models = load_models()
            xgb_model = models.get('xgb')
            lstm_model = models.get('lstm')

            # Загрузка препроцессора
            preprocessor_path = os.path.join(settings.MODELS_DIR, 'preprocessor.pkl')
            preprocessor = joblib.load(preprocessor_path) if os.path.exists(preprocessor_path) else None

            if xgb_model is None or preprocessor is None:
                logger.error("Модели или препроцессор не загружены")
                return None

            if should_use_xgb(self.status.type):
                # XGBoost модель
                input_data = self._prepare_prediction_input()
                processed_input = preprocessor.transform([input_data])
                seconds = xgb_model.predict(processed_input)[0]
            else:
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
        # Получаем завершённые задачи
        completed_tasks = Task.objects.filter(
            status__type='completed',
            start_time__isnull=False
        ).order_by('start_time')

        if not completed_tasks.exists():
            logger.warning("Нет завершенных задач для LSTM")
            return None
        # Время первой задачи — базовая точка отсчёта
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
