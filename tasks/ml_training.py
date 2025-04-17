from tasks.ml_data_preparer import PreparedData
import logging
import torch

logger = logging.getLogger(__name__)


def train_model():
    """
    Главная функция для обучения моделей XGBoost и LSTM.
    Подготавливает данные, обучает модели, сохраняет их и возвращает метрики.
    """
    from task_tracker.settings import MIN_SAMPLES, LSTM_TIMESTEPS
    from tasks.ml_data_preparer import prepare_for_xgb

    logger.info("Запуск обучения модели...")

    try:
        # Подготовка данных
        data = prepare_for_xgb(task_ids=None)
        if data is None:
            raise ValueError("Нет данных для обучения")
        logger.debug(f"Количество примеров после подготовки: {len(data.x)}")

        # Проверка на минимальное количество примеров
        if len(data.x) < MIN_SAMPLES:
            logger.warning("Недостаточно данных. Использую резервную модель")
            create_fallback_models()
            return {'status': 'warning', 'message': 'Not enough data'}

        # Обучение модели XGBoost
        xgb_model, xgb_metrics = train_xgb(data)
        logger.info("XGBoost обучение завершено.")
        logger.debug(f"XGBoost метрики: {xgb_metrics}")

        # Подготовка данных для LSTM
        x_seq, y_seq = train_lstm_prepare(data)

        lstm_model = None
        lstm_metrics = {}

        # Обучение LSTM при наличии достаточного количества последовательностей
        if len(x_seq) >= LSTM_TIMESTEPS:
            lstm_model, lstm_metrics = train_lstm(x_seq, y_seq)
            logger.info("LSTM обучение завершено.")
        else:
            logger.warning("Недостаточно последовательностей для LSTM обучения.")

        # Сохранение обученных моделей и препроцессора
        save_models(xgb_model, lstm_model, data.preprocessor)
        logger.info("Модели сохранены успешно.")

        return {'status': 'success', **xgb_metrics, **lstm_metrics}

    except Exception as e:
        logger.exception("Ошибка при обучении моделей.")
        create_fallback_models()
        return {'status': 'error', 'message': str(e)}


def train_xgb(data: PreparedData):
    """
    Обучение модели XGBoost и расчёт метрик.
    """
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    import xgboost as xgb

    logger.info("Обучение XGBoost модели...")
    model = xgb.XGBRegressor(objective='reg:squarederror')
    model.fit(data.x, data.y)

    pred = model.predict(data.x)
    metrics = {
        'mse': mean_squared_error(data.y, pred),
        'mae': mean_absolute_error(data.y, pred)
    }

    logger.debug(f"XGBoost метрики: {metrics}")
    return model, metrics


def train_lstm_prepare(data: PreparedData):
    """
    Преобразует данные в формат последовательностей для LSTM.
    Каждая последовательность состоит из `LSTM_TIMESTEPS` подряд идущих шагов.
    """
    import numpy as np
    from task_tracker.settings import LSTM_TIMESTEPS

    logger.info("Подготовка последовательностей для LSTM...")

    if data is None or not hasattr(data, 'x') or not hasattr(data, 'y'):
        logger.error("Неверный формат данных: отсутствуют x или y.")
        return np.array([]), np.array([])

    x_raw = data.x
    y_raw = data.y

    logger.debug(f"Размерности: x = {x_raw.shape}, y = {len(y_raw)}, TIMESTEPS = {LSTM_TIMESTEPS}")

    if len(x_raw) <= LSTM_TIMESTEPS:
        logger.warning(f"Недостаточно примеров для формирования хотя бы одной последовательности LSTM (нужно > {LSTM_TIMESTEPS})")
        return np.array([]), np.array([])

    sequences = []
    targets = []

    # Формирование окон последовательностей и соответствующих таргетов
    for i in range(len(x_raw) - LSTM_TIMESTEPS):
        x_seq = x_raw[i:i + LSTM_TIMESTEPS]
        y_target = y_raw[i + LSTM_TIMESTEPS] if i + LSTM_TIMESTEPS < len(y_raw) else None

        if y_target is None:
            logger.warning(f"Нет y для последовательности, i={i}")
            continue

        sequences.append(x_seq)
        targets.append(y_target)

    x_seq = np.array(sequences)
    y_seq = np.array(targets)

    logger.debug(f"LSTM: подготовлено {len(x_seq)} последовательностей и {len(y_seq)} таргетов")
    return x_seq, y_seq


class LSTMModel(torch.nn.Module):
    """
    Простая LSTM-модель с одним слоем LSTM и полносвязным выходом.
    """
    def __init__(self, input_size, hidden_size):
        super().__init__()
        self.lstm = torch.nn.LSTM(input_size, hidden_size, batch_first=True)
        self.linear = torch.nn.Linear(hidden_size, 1)

    def forward(self, x):
        out, _ = self.lstm(x)
        return self.linear(out[:, -1, :])


def train_lstm(x_seq, y_seq):
    """
    Обучение LSTM модели
    """
    import torch
    import torch.nn as nn
    import torch.optim as optim
    from torch.utils.data import DataLoader, TensorDataset

    logger.info("Обучение LSTM модели с PyTorch...")

    # Преобразование данных в тензоры
    X_tensor = torch.FloatTensor(x_seq)
    y_tensor = torch.FloatTensor(y_seq).view(-1, 1)

    dataset = TensorDataset(X_tensor, y_tensor)
    loader = DataLoader(dataset, batch_size=32, shuffle=True)

    model = LSTMModel(input_size=x_seq.shape[2], hidden_size=64)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    model.train()
    for epoch in range(50):
        epoch_loss = None
        for batch_x, batch_y in loader:
            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            epoch_loss = loss.item()

        if epoch % 10 == 0 and epoch_loss is not None:
            logger.info(f'Epoch {epoch}, Loss: {epoch_loss:.4f}')

    logger.info("LSTM обучение завершено.")
    return model, {'lstm_status': 'trained'}


def save_models(xgb_model, lstm_model, preprocessor):
    """
    Сохраняет модели и препроцессор в файловую систему.
    """
    import os
    import joblib
    from task_tracker.settings import MODELS_DIR

    logger.info("Сохранение моделей...")

    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)
        logger.debug(f"Создана директория для моделей: {MODELS_DIR}")

    joblib.dump(xgb_model, f'{MODELS_DIR}/xgb_model.pkl')
    joblib.dump(preprocessor, f'{MODELS_DIR}/preprocessor.pkl')

    if lstm_model:
        torch.save(lstm_model.state_dict(), f'{MODELS_DIR}/lstm_model.pth')

    logger.info("Модели успешно сохранены.")


def create_fallback_models():
    """
    Создаёт и сохраняет резервную XGBoost модель.
    Используется в случае ошибок или недостатка данных.
    """
    from task_tracker.settings import MODELS_DIR
    import xgboost as xgb
    import numpy as np

    logger.warning("Создание резервной модели XGBoost...")

    try:
        x = np.random.rand(10, 4)
        y = np.random.rand(10)
        model = xgb.XGBRegressor()
        model.fit(x, y)

        model.save_model(f'{MODELS_DIR}/xgb_fallback.pkl')
        logger.info("Резервная модель создана")

    except Exception as e:
        logger.error(f"Ошибка при создании резервной модели: {e}")
