from datetime import datetime
from typing import List, TYPE_CHECKING
import logging
logger = logging.getLogger(__name__)

def get_category_avg_duration(categories):
    from django.core.cache import cache
    from tasks.models import Task
    if not categories:
        return 0

    if not isinstance(categories, (list, tuple, set)):
        categories = [categories]

    category_ids = sorted([cat.id for cat in categories])
    cache_key = f"avg_duration:{'-'.join(map(str, category_ids))}"

    cached_value = cache.get(cache_key)
    if cached_value is not None:
        return cached_value

    tasks = Task.objects.filter(
        category__in=categories,
        status__type='completed',
        start_time__isnull=False,
        end_time__isnull=False
    ).only('start_time', 'end_time')

    total_seconds = 0
    count = tasks.count()

    if count == 0:
        return 0

    for task in tasks:
        duration = task.end_time - task.start_time
        total_seconds += duration.total_seconds()

    avg_seconds = total_seconds / count
    cache.set(cache_key, avg_seconds, timeout=3600)

    return avg_seconds

def should_use_xgb(status_name: str) -> bool:
    return status_name in ['required check', 'planned']


if TYPE_CHECKING:
    from tasks.models import Task

def extract_task_features(task: 'Task', base_time: datetime = None) -> List[float]:
    try:
        from django.db.models import Subquery
        from tasks.models import Task, Executor

        executor_subquery = Executor.objects.filter(task_id=task.id).order_by('id').values('employee__current_load')[:1]
        current_load = Task.objects.filter(id=task.id).annotate(
            load=Subquery(executor_subquery)
        ).values_list('load', flat=True).first() or 0

        priority_weight = task.priority.get_weight() if task.priority else 0.0
        category_avg = get_category_avg_duration(task.category) if task.category else 0.0
        description_length = len(task.description) if task.description else 0

        if base_time and task.start_time:
            time_diff = (task.start_time - base_time).total_seconds()
        else:
            time_diff = 0.0

        return [priority_weight, current_load, category_avg, description_length, time_diff]

    except Exception as e:
        logger.exception(f"Ошибка при извлечении признаков задачи {task.id}: {e}")
        return [0.0, 0.0, 0.0, 0.0, 0.0]
