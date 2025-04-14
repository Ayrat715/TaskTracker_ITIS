from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
import logging
from tasks.models import Task
logger = logging.getLogger(__name__)

@receiver(pre_save, sender=Task)
def classify_task(sender, instance, **kwargs):
    from tasks.ml_category import classifier
    from tasks.models import TaskCategory

    logger.debug(
        f"Starting classification for task {instance.id} "
        f"(New: {instance._state.adding})"
    )

    try:
        tracker = instance.tracker
        if instance._state.adding:
            classify = True
            logger.debug("New task, classification required")
        else:
            changed_fields = tracker.changed()
            classify = 'name' in changed_fields or 'description' in changed_fields
            logger.debug(
                f"Existing task. Changed fields: {changed_fields}. "
                f"Classification needed: {classify}"
            )

        if classify and instance.name and instance.description:
            logger.info(
                f"Classifying task {instance.id} "
                f"with title: '{instance.name[:50]}...'"
            )

            text_input = f"{instance.name} {instance.description}"
            predicted_category = classifier.predict_category(text_input)

            logger.debug(f"Predicted category: {predicted_category}")

            if predicted_category:
                category, created = TaskCategory.objects.get_or_create(
                    name=predicted_category,
                    defaults={'description': predicted_category}
                )

                log_msg = (
                    f"Assigned category '{predicted_category}' (ID: {category.id}) "
                    f"to task {instance.id}"
                )
                if created:
                    logger.warning(f"Created new category: {predicted_category}")
                    log_msg += " [NEW CATEGORY]"

                logger.info(log_msg)
                instance.category = category
            else:
                logger.warning(
                    f"No category predicted for task {instance.id}. "
                    f"Using default category."
                )

    except Exception as e:
        logger.error(
            f"Classification failed for task {instance.id}: {str(e)}",
            exc_info=True
        )
        raise


@receiver(post_save, sender=Task)
def retrain_model_on_task_completion(sender, instance, **kwargs):
    from tasks.ml_training import train_model
    if instance.status and instance.status.type == 'completed':
        logger.info(
            f"Detected completed task {instance.id}. "
            f"Checking if retraining is needed..."
        )

        try:
            logger.info(f"Starting model retraining after task {instance.id} completion")
            result = train_model()

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