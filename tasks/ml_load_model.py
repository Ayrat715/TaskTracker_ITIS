import logging
import os
import joblib

logger = logging.getLogger(__name__)

REQUIRED_MODELS = {
    'xgb': ('xgb_model.pkl', joblib.load),
    'lstm': (
        'lstm_model.pth',
        lambda path: load_lstm_model(path)
    )
}

def load_models():
    from tasks.ml_training import train_model
    logger.info("Загрузка моделей...")
    models = {
        key: _load_single_model(filename, loader)
        for key, (filename, loader) in REQUIRED_MODELS.items()
    }

    if any(m is None for m in models.values()):
        logger.warning("Одна или несколько моделей не загружены. Запуск обучения...")
        train_model()
        return load_models()

    logger.info("Все модели успешно загружены.")
    return models


def _load_single_model(filename, loader):
    from task_tracker.settings import MODELS_DIR
    path = os.path.join(MODELS_DIR, filename)
    try:
        if os.path.exists(path):
            logger.info(f"Загрузка модели: {filename}")
            return loader(path)
        else:
            logger.warning(f"Файл модели не найден: {filename}")
    except Exception as e:
        logger.error(f"Ошибка при загрузке {filename}: {e}")
    return None

def load_lstm_model(path):
    from tasks.ml_training import LSTMModel
    import torch
    model = LSTMModel(input_size=4, hidden_size=64)
    model.load_state_dict(torch.load(path))
    model.eval()
    return model