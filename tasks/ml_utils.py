from datetime import datetime
from typing import List, TYPE_CHECKING
import logging

logger = logging.getLogger(__name__)

# Функция рассчитывает среднюю длительность выполнения задач в указанных категориях
def get_category_avg_duration(categories):
    from django.core.cache import cache
    from tasks.models import Task

    if not categories:
        return 0  # Если категории не указаны, возвращаем 0

    # Преобразуем одиночную категорию в список
    if not isinstance(categories, (list, tuple, set)):
        categories = [categories]

    # Формируем ключ для кэша из отсортированных id категорий
    category_ids = sorted([cat.id for cat in categories])
    cache_key = f"avg_duration:{'-'.join(map(str, category_ids))}"

    # Проверка наличия значения в кэше
    cached_value = cache.get(cache_key)
    if cached_value is not None:
        return cached_value  # Если есть, возвращаем его

    # Фильтруем задачи, завершённые и с указанным временем начала и конца
    tasks = Task.objects.filter(
        category__in=categories,
        status__type='completed',
        start_time__isnull=False,
        end_time__isnull=False
    ).only('start_time', 'end_time')

    total_seconds = 0
    count = tasks.count()

    if count == 0:
        return 0  # Нет задач — возвращаем 0

    # Суммируем длительности всех задач
    for task in tasks:
        duration = task.end_time - task.start_time
        total_seconds += duration.total_seconds()

    # Считаем среднюю длительность
    avg_seconds = total_seconds / count

    # Сохраняем результат в кэш на 1 час
    cache.set(cache_key, avg_seconds, timeout=3600)

    return avg_seconds

# Импортируем модель Task только при проверке типов(чтобы избежать циклических импортов)
if TYPE_CHECKING:
    from tasks.models import Task

# Извлечение признаков задачи для ML-модели
def extract_task_features(task: 'Task', base_time: datetime = None) -> List[float]:
    try:
        from django.db.models import Subquery
        from tasks.models import Task, Executor

        # Получение текущей нагрузки первого исполнителя задачи через подзапрос
        executor_subquery = Executor.objects.filter(task_id=task.id).order_by('id').values('employee__current_load')[:1]
        current_load = Task.objects.filter(id=task.id).annotate(
            load=Subquery(executor_subquery)
        ).values_list('load', flat=True).first() or 0

        # Получение веса приоритета задачи
        priority_weight = task.priority.get_weight() if task.priority else 0.0

        # Получение средней длительности по категории
        category_avg = get_category_avg_duration(task.category) if task.category else 0.0

        # Длина описания задачи
        description_length = len(task.description) if task.description else 0

        # Разница во времени между базовой точкой и временем начала задачи
        if base_time and task.start_time:
            time_diff = (task.start_time - base_time).total_seconds()
        else:
            time_diff = 0.0

        # Возвращаем список признаков
        return [priority_weight, current_load, category_avg, description_length, time_diff]

    except Exception as e:
        logger.exception(f"Ошибка при извлечении признаков задачи {task.id}: {e}")
        # В случае ошибки возвращаем нулевые значения
        return [0.0, 0.0, 0.0, 0.0, 0.0]

