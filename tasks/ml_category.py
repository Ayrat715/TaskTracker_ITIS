import logging
import os
from django.conf import settings
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from joblib import dump, load
from .models import Task
logger = logging.getLogger(__name__)

class CategoryClassifier:
    def __init__(self):
        self.vectorizer = None
        self.model = None
        self.model_path = os.path.join(settings.BASE_DIR, 'models', 'category_model.joblib')
        self.vectorizer_path = os.path.join(settings.BASE_DIR, 'models', 'vectorizer.joblib')
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        logger.info("Инициализация CategoryClassifier")
        self._load_or_train()

    def _load_or_train(self):
        try:
            self.vectorizer = load(self.vectorizer_path)
            self.model = load(self.model_path)
            logger.info("Модель и векторизатор успешно загружены")
        except Exception as e:
            logger.warning(f"Не удалось загрузить модель или векторизатор: {e}. Выполняется начальное обучение.")
            self._train_initial()

    def _train_initial(self):
        logger.info("Запуск начального обучения модели")
        self.train()

    def train(self):
        tasks = Task.objects.all()
        if not tasks.exists():
            logger.warning("Нет задач для обучения модели")
            return

        texts = []
        labels = []
        for t in tasks:
            name = t.name or ''
            desc = t.description or ''
            text = f"{name} {desc}".strip()
            if not text:
                continue
            if t.category and t.category.name:
                texts.append(text)
                labels.append(t.category.name)

        if not texts:
            logger.warning("Нет текстов с категориями для обучения")
            return

        logger.info(f"Обучение модели на {len(texts)} примерах")
        self.vectorizer = TfidfVectorizer()
        X = self.vectorizer.fit_transform(texts)
        self.model = LogisticRegression(max_iter=1000)
        self.model.fit(X, labels)
        dump(self.vectorizer, self.vectorizer_path)
        dump(self.model, self.model_path)
        logger.info("Модель и векторизатор сохранены")

    def predict(self, task):
        if not self.model or not self.vectorizer:
            logger.warning("Попытка предсказания без загруженной модели или векторизатора")
            return None, 0.0

        name = task.name or ''
        desc = task.description or ''
        text = f"{name} {desc}".strip()
        if not text:
            logger.warning("Пустой текст задачи, пропуск предсказания")
            return None, 0.0

        try:
            X = self.vectorizer.transform([text])
            prediction = self.model.predict(X)
            proba = self.model.predict_proba(X)[0]
            confidence = max(proba)
            logger.info(f"Предсказана категория '{prediction[0]}' с уверенностью {confidence:.2f} для задачи ID={task.id}")
            return prediction[0], confidence
        except Exception as e:
            logger.error(f"Ошибка при предсказании: {e}")
            return None, 0.0

def keyword_matcher(task, categories):
    logger.info(f"Запуск keyword_matcher для задачи ID={task.id}")
    name = task.name or ''
    desc = task.description or ''
    text = f"{name} {desc}".lower()
    for category in categories:
        for keyword in category.processed_keywords:
            if keyword and keyword.lower() in text:
                logger.info(f"Ключевое слово '{keyword}' найдено в задаче ID={task.id}, категория: {category.name}")
                return category
    logger.info(f"Ключевые слова не найдены для задачи ID={task.id}")
    return None
