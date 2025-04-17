import logging

logger = logging.getLogger(__name__)


class MyDataPreparer:
    @staticmethod
    def get_completed_tasks(task_ids=None):
        from tasks.models import Task
        from django.db.models import F
        from django.db.models.functions import Extract

        logger.info("Получение завершённых задач...")

        # Получаем завершённые задачи, при необходимости фильтруем по переданным task_ids
        if task_ids is not None:
            tasks = Task.objects.filter(
                id__in=task_ids,
                status__type='completed',
                start_time__isnull=False,
                end_time__isnull=False
            )
        else:
            tasks = Task.objects.filter(
                status__type='completed',
                start_time__isnull=False,
                end_time__isnull=False
            )

        # Вычисляем длительность задач в секундах
        tasks = tasks.annotate(
            duration_sec=Extract(F('end_time') - F('start_time'), 'epoch')
        )

        logger.debug(f"Получено {tasks.count()} завершённых задач.")
        return tasks


class PreparedData:
    """
    Контейнер для хранения подготовленных данных:
    - x: признаки
    - y: целевые значения
    - preprocessor: объект предобработки
    """
    def __init__(self, x, y, preprocessor):
        self.x = x
        self.y = y
        self.preprocessor = preprocessor


def prepare_for_lstm(task_ids):
    """
    Подготовка данных для LSTM модели.
    Возвращает numpy-массивы признаков (x) и целевых значений (y).
    """
    import numpy as np
    from tasks.ml_utils import extract_task_features

    logger.info("Подготовка данных для LSTM модели...")

    if not task_ids:
        logger.error("task_ids не переданы в prepare_for_lstm")

    # Получаем задачи, отсортированные по времени начала
    tasks = MyDataPreparer.get_completed_tasks(task_ids).order_by('start_time')

    if not tasks:
        logger.warning("Нет завершённых задач для подготовки LSTM.")

    x, y = [], []
    # Определяем базовое время относительно начала первой задачи
    start_time = tasks.first().start_time if tasks else None

    if not start_time:
        logger.error("start_time не удалось определить для LSTM.")

    # Извлекаем признаки и целевые значения для каждой задачи
    for task in tasks:
        features = extract_task_features(task, base_time=start_time)
        x.append(features)
        y.append(task.duration_sec)

    logger.debug(f"LSTM: подготовлено {len(x)} примеров.")
    return np.array(x), np.array(y)


def prepare_for_xgb(task_ids=None):
    """
    Подготовка данных для XGBoost модели.
    Возвращает объект PreparedData, содержащий признаки, целевые значения и препроцессор.
    """
    from tasks.ml_utils import extract_task_features
    from sklearn.preprocessing import StandardScaler

    logger.info("Подготовка данных для XGBoost модели...")

    # Получаем задачи
    tasks = MyDataPreparer.get_completed_tasks(task_ids)

    if not tasks.exists():
        logger.warning("Нет завершённых задач для подготовки XGBoost.")
        return None

    x, y = [], []
    for task in tasks:
        duration = getattr(task, 'duration_sec', None)

        # Пропускаем задачи без продолжительности
        if duration is None:
            logger.warning(f"У задачи {task.id} нет поля duration_sec.")
            continue

        # Извлекаем признаки, пропускаем при неудаче
        features = extract_task_features(task)
        if features is None:
            logger.warning(f"Не удалось извлечь признаки из задачи {task.id}.")
            continue

        # Для XGBoost используем не все признаки, возможно, последний является меткой
        x.append(features[:-1])
        y.append(duration)

    if not x:
        logger.warning("Нет данных для обучения модели XGBoost.")
        return None

    # Нормализуем признаки
    preprocessor = StandardScaler()
    x_scaled = preprocessor.fit_transform(x)

    logger.debug(f"XGBoost: подготовлено {len(x)} примеров.")
    return PreparedData(x_scaled, y, preprocessor)

