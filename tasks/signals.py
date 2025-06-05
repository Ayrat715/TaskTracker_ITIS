from django.db.models.signals import post_save
from django.dispatch import receiver
import logging
from yake import KeywordExtractor
from keybert import KeyBERT
from tasks.ml_category import keyword_matcher, CategoryClassifier
from tasks.models import Task, TaskCategory
logger = logging.getLogger(__name__)

@receiver(post_save, sender=Task)
def categorize_task(sender, instance, created, **kwargs):
    """
    Сигнал, который автоматически срабатывает после сохранения новой задачи.
    Производит попытку категоризации: сначала по ключевым словам,
    потом с помощью ML-классификатора, иначе создаёт новую категорию.
    """
    if not created:
        return

    task = instance
    logger.info(f"Запущена автокатегоризация для задачи ID={task.id}")

    categories = TaskCategory.objects.all()
    matched_category = keyword_matcher(task, categories)
    if matched_category:
        task.category = matched_category
        task.save()
        logger.info(f"Категория найдена по ключевым словам: {matched_category.name} для задачи ID={task.id}")
        return

    classifier = CategoryClassifier()
    predicted_category_name, confidence = classifier.predict(task)

    if predicted_category_name and confidence > 0.8:
        logger.info(
            f"ML-классификатор предсказал категорию '{predicted_category_name}' с уверенностью {confidence:.2f} для задачи ID={task.id}")
        try:
            category = TaskCategory.objects.get(name=predicted_category_name)
        except TaskCategory.DoesNotExist:
            category = TaskCategory.objects.create(
                name=predicted_category_name,
                description=f"Автоматически созданная категория (ML, уверенность: {confidence:.2f})"
            )
        task.category = category
        task.save()
        logger.info(f"Категория присвоена по ML: {predicted_category_name} для задачи ID={task.id}")
        return

    extractor = KeywordExtractor(lan="ru", n=3, top=3)
    keywords = extractor.extract_keywords(task.description or '')
    if keywords:
        name = keywords[0][0]
        logger.info(f"YAKE выделил ключевые слова: {[kw[0] for kw in keywords]}")
    else:
        logger.warning(f"YAKE не нашёл ключевых слов для задачи ID={task.id}, используется KeyBERT")
        kw_model = KeyBERT(model='all-MiniLM-L6-v2')
        description = task.description or task.name
        keyphrases = kw_model.extract_keywords(description or '', keyphrase_ngram_range=(1, 2), top_n=3)
        name = keyphrases[0][0] if keyphrases else task.name[:50] if task.name else "Новая категория"
        logger.info(f"KeyBERT выделил ключевые фразы: {[kp[0] for kp in keyphrases]}")

    new_category = TaskCategory.objects.create(
        name=name,
        description='Автоматически сгенерированная категория',
        keywords=', '.join([kw[0] for kw in keywords]) if keywords else ''
    )
    task.category = new_category
    task.save()
    logger.info(f"Создана новая категория '{name}' для задачи ID={task.id}")


@receiver(post_save, sender=Task)
def retrain_model_on_task_completion(sender, instance, **kwargs):
    """
    Сигнал, вызываемый после сохранения задачи.
    Если задача завершена, инициирует переобучение модели.
    """
    from tasks.ml_training import train_model

    # Проверяем, что задача завершена
    if instance.status and instance.status.type == 'completed':
        logger.info(
            f"Detected completed task {instance.id}. "
            f"Checking if retraining is needed..."
        )

        try:
            logger.info(f"Starting model retraining after task {instance.id} completion")
            result = train_model()  # Запускаем переобучение модели

            # Обрабатываем результат обучения
            if result.get('status') == 'success':
                logger.info(
                    "Model retraining completed successfully. "
                    f"MSE: {result.get('mse', 'N/A')}, "
                    f"MAE: {result.get('mae', 'N/A')}"
                )
            else:
                logger.error(
                    "Model retraining failed. "
                    f"Error: {result.get('message', 'Unknown error')}"
                )

        except Exception as e:
            logger.critical(
                f"Critical error during model retraining after task {instance.id}: {str(e)}",
                exc_info=True
            )
            raise
