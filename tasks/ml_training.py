from tasks.ml_data_preparer import PreparedData
import logging
logger = logging.getLogger(__name__)


def train_model():
    from task_tracker.settings import MIN_SAMPLES, LSTM_TIMESTEPS
    from tasks.ml_data_preparer import prepare_for_xgb

    logger.info("Запуск обучения модели...")

    try:
        data = prepare_for_xgb(task_ids=None)
        if data is None:
            raise ValueError("Нет данных для обучения")
        logger.debug(f"Количество примеров после подготовки: {len(data.x)}")

        if len(data.x) < MIN_SAMPLES:
            logger.warning("Недостаточно данных. Использую резервную модель")
            create_fallback_models()
            return {'status': 'warning', 'message': 'Not enough data'}

        xgb_model, xgb_metrics = train_xgb(data)
        logger.info("XGBoost обучение завершено.")
        logger.debug(f"XGBoost метрики: {xgb_metrics}")

        x_seq, y_seq = train_lstm_prepare(data)

        lstm_model = None
        lstm_metrics = {}

        if len(x_seq) >= LSTM_TIMESTEPS:
            lstm_model, lstm_metrics = train_lstm(x_seq, y_seq)
            logger.info("LSTM обучение завершено.")
        else:
            logger.warning("Недостаточно последовательностей для LSTM обучения.")

        save_models(xgb_model, lstm_model, data.preprocessor)
        logger.info("Модели сохранены успешно.")

        return {'status': 'success', **xgb_metrics, **lstm_metrics}

    except Exception as e:
        logger.exception("Ошибка при обучении моделей.")
        create_fallback_models()
        return {'status': 'error', 'message': str(e)}


def train_xgb(data: PreparedData):
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
    import numpy as np
    from sklearn.preprocessing import StandardScaler
    from task_tracker.settings import LSTM_TIMESTEPS

    logger.info("Подготовка последовательностей для LSTM...")

    scaler = StandardScaler()
    scaled_x = scaler.fit_transform(data.x)
    sequences = []

    for i in range(len(scaled_x) - LSTM_TIMESTEPS):
        sequences.append(scaled_x[i:i + LSTM_TIMESTEPS])

    x_seq = np.array(sequences)
    y_seq = np.array(data.y[LSTM_TIMESTEPS:])

    logger.debug(f"LSTM последовательностей подготовлено: {len(x_seq)}")
    return x_seq, y_seq


def train_lstm(x_seq, y_seq):
    from keras import Sequential
    from keras.src.callbacks import EarlyStopping
    from keras.src.layers import Dense
    from keras.src.optimizers import Adam
    from keras.src.layers import LSTM

    logger.info("Обучение LSTM модели...")

    model = Sequential([
        LSTM(64, input_shape=(x_seq.shape[1], x_seq.shape[2])),
        Dense(1)
    ])
    model.compile(optimizer=Adam(0.001), loss='mse')
    model.fit(x_seq, y_seq, epochs=50, batch_size=32,
              callbacks=[EarlyStopping(patience=5)])

    logger.info("LSTM обучение завершено.")
    return model, {'lstm_status': 'trained'}


def save_models(xgb_model, lstm_model, preprocessor):
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
        lstm_model.save(f'{MODELS_DIR}/lstm_model.h5')

    logger.info("Модели успешно сохранены.")


def create_fallback_models():
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
