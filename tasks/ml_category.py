import logging
from django.conf import settings
from django.db import transaction
from celery import shared_task
from task_tracker.settings import MODELS_DIR, PREDICTION_CONFIDENCE, PREDICTION_ERRORS
from .text_processing import preprocess, nlp_ru

logger = logging.getLogger(__name__)


DEFAULT_CATEGORY = 'Другое'
KEYWORD_UPDATE_INTERVAL = getattr(settings, 'KEYWORD_UPDATE_INTERVAL', 3600)


# Метод по умолчанию, если не удаётся определить категорию
def _fallback_method(text):
    return DEFAULT_CATEGORY


# Классификатор категорий
class CategoryClassifier:

    def __init__(self):
        self._verify_dependencies()
        self.model = None
        self.vectorizer = None
        self.w2v_model = None
        self.classes = [DEFAULT_CATEGORY]
        self.is_trained = False
        self.keyword_categories = []
        self.last_keyword_update = None
        self.refresh_keywords()  # Загружаем ключевые слова категорий
        self.initialize_model()  # Загружаем/создаём модель

    def _verify_dependencies(self):
        if not hasattr(nlp_ru, 'pipe'):
            raise RuntimeError("Spacy models not initialized")

    def initialize_model(self):
        try:
            self.load_models()  # Пытаемся загрузить обученные модели
            self.is_trained = True
        except Exception as e:
            logger.warning(f"Models not found, initializing default: {e}")
            self.create_initial_model()  # Создаём начальную модель
            self.is_trained = False

    def create_initial_model(self):
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.svm import LinearSVC
            from tasks.models import TaskCategory
            import os

            logger.info("Creating initial dummy model...")

            # Создаём категорию по умолчанию, если её нет
            TaskCategory.objects.get_or_create(
                name=DEFAULT_CATEGORY,
                defaults={'description': 'Категория по умолчанию'}
            )

            # Используем другие категории, если они есть
            categories = TaskCategory.objects.exclude(name=DEFAULT_CATEGORY)
            if not categories.exists():
                logger.info("Only default category exists, skipping model creation.")
                return

            all_categories = TaskCategory.objects.all()
            category_names = [cat.name for cat in all_categories]

            os.makedirs(MODELS_DIR, exist_ok=True)
            texts = [f"Пример задачи для категории {cat.name}" for cat in all_categories]
            labels = [cat.name for cat in all_categories]

            # Векторизация и обучение начальной модели
            vectorizer = TfidfVectorizer()
            X = vectorizer.fit_transform(texts)
            model = LinearSVC()
            model.fit(X, labels)

            self.save_artifacts(
                model=model,
                vectorizer=vectorizer,
                w2v_model=None,
                classes=category_names,
                version='initial'
            )

            logger.info("Initial model created successfully.")

        except Exception as e:
            logger.exception(f"Failed to create initial model: {e}")

    # Обновление списка ключевых слов категорий
    def refresh_keywords(self):
        from django.utils import timezone
        from tasks.models import TaskCategory

        self.keyword_categories = list(
            TaskCategory.objects.exclude(processed_keywords__exact='')
            .exclude(name=DEFAULT_CATEGORY)
            .only('name', 'processed_keywords')
        )
        self.last_keyword_update = timezone.now()

    # Загрузка модели и артефактов
    def load_models(self):
        import os
        import joblib
        from gensim.models import Word2Vec

        required_files = ['model.pkl', 'vectorizer.pkl', 'classes.pkl']
        for fname in required_files:
            path = os.path.join(MODELS_DIR, fname)
            if not os.path.exists(path):
                raise FileNotFoundError(f"Missing model file: {fname}")

        logger.info(f"Loading models from: {MODELS_DIR}")

        self.model = joblib.load(os.path.join(MODELS_DIR, 'model.pkl'))
        self.vectorizer = joblib.load(os.path.join(MODELS_DIR, 'vectorizer.pkl'))
        self.classes = joblib.load(os.path.join(MODELS_DIR, 'classes.pkl'))

        w2v_path = os.path.join(MODELS_DIR, 'w2v.model')
        if os.path.exists(w2v_path):
            self.w2v_model = Word2Vec.load(w2v_path)
            self.w2v_model.init_sims(replace=True)

    # Сохранение обученной модели и вспомогательных объектов
    def save_artifacts(self, **artifacts):
        import os
        import shutil
        import joblib
        from django.utils import timezone
        from django.core.management import call_command

        version = artifacts.get('version', timezone.now().strftime("%Y%m%d%H%M%S"))
        call_command('clean_old_models')  # Удаление старых моделей

        # Сохраняем файлы
        joblib.dump(artifacts['model'], os.path.join(MODELS_DIR, f'model_{version}.pkl'))
        joblib.dump(artifacts['vectorizer'], os.path.join(MODELS_DIR, f'vectorizer_{version}.pkl'))
        joblib.dump(artifacts['classes'], os.path.join(MODELS_DIR, f'classes_{version}.pkl'))

        if artifacts['w2v_model']:
            artifacts['w2v_model'].save(os.path.join(MODELS_DIR, f'w2v_{version}.model'))

        # Обновляем симлинки на актуальные модели
        for name in ['model', 'vectorizer', 'classes']:
            src = os.path.join(MODELS_DIR, f'{name}_{version}.pkl')
            dst = os.path.join(MODELS_DIR, f'{name}.pkl')
            if os.path.exists(dst):
                os.remove(dst)
            try:
                os.symlink(src, dst)
            except OSError:
                shutil.copyfile(src, dst)

    # Получение векторного представления текста из Word2Vec
    def _get_w2v_features(self, text):
        import numpy as np
        if not self.w2v_model:
            return np.zeros((1, 100))
        vectors = [self.w2v_model.wv[word] for word in text.split() if word in self.w2v_model.wv]
        if vectors:
            return np.mean(vectors, axis=0).reshape(1, -1)
        return np.zeros((1, self.w2v_model.vector_size))

    # Предсказание категории по тексту
    def predict_category(self, text):
        import numpy as np
        from django.utils import timezone
        from django.core.cache import cache

        cache_key = f'category:{hash(text)}'
        if cached := cache.get(cache_key):
            return cached

        try:
            processed_text = preprocess(text)
            processed_lemmas = set(processed_text.split())

            # Обновление ключевых слов по таймеру
            if (timezone.now() - self.last_keyword_update).total_seconds() > KEYWORD_UPDATE_INTERVAL:
                self.refresh_keywords()

            # Пытаемся сопоставить по ключевым словам
            best_match = None
            max_matches = 0

            for category in self.keyword_categories:
                matches = 0
                for keyword_group in category.processed_keywords.split(','):
                    if not keyword_group:
                        continue
                    required_lemmas = keyword_group.split()
                    if all(lemma in processed_lemmas for lemma in required_lemmas):
                        matches += 1

                if matches > max_matches:
                    max_matches = matches
                    best_match = category.name

            if best_match:
                cache.set(cache_key, best_match, timeout=300)
                return best_match

            # Классификация через модель
            if len(self.classes) == 1 and self.classes[0] == DEFAULT_CATEGORY:
                return DEFAULT_CATEGORY
            X = self.vectorizer.transform([processed_text])
            proba = self.model.decision_function(X)
            index = np.argmax(proba)
            max_proba = proba[0][index] if hasattr(proba[0], '__getitem__') else proba[index]
            PREDICTION_CONFIDENCE.set(max_proba)
            result = self.classes[index]
            cache.set(cache_key, result, timeout=300)
            return result

        except Exception as e:
            PREDICTION_ERRORS.inc()
            logger.warning(f"Primary method failed: {e}")
            return _fallback_method(text)


# Присваивание категории задаче
@shared_task
def assign_category(task_id):
    from filelock import FileLock
    from tasks.models import Task

    task = Task.objects.get(id=task_id)
    classifier = CategoryClassifier()

    with FileLock("model_update.lock"):  # Блокировка, чтобы избежать одновременного обновления модели
        category = classifier.predict_category(task.description)
        task.category = category
        task.save(update_fields=["category"])


# Переобучение модели
@shared_task
@transaction.atomic
def retrain_classifier():
    from task_tracker.settings import MIN_SAMPLES
    from django.utils import timezone
    from gensim.models import Word2Vec
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.model_selection import train_test_split
    from sklearn.svm import LinearSVC
    from sklearn.utils import compute_class_weight
    import numpy as np
    from .models import Task

    tasks = Task.objects.filter(category__isnull=False)
    logger.info(f"Training data: {[(t.id, t.category.name) for t in tasks]}")

    if tasks.count() < MIN_SAMPLES:
        logger.info(f"Not enough samples ({tasks.count()}), using default model")
        return

    # Подготовка данных
    texts = [preprocess(f"{t.name} {t.description}") for t in tasks]
    labels = [t.category.name for t in tasks]

    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    x_tfidf = vectorizer.fit_transform(texts)

    # Обучение Word2Vec при наличии достаточного количества данных
    w2v_model = None
    if len(texts) >= 100:
        sentences = [text.split() for text in texts]
        w2v_model = Word2Vec(
            sentences,
            vector_size=100,
            window=5,
            min_count=3,
            workers=4,
            epochs=10
        )

    # Комбинирование признаков
    X = x_tfidf.toarray()
    if w2v_model:
        x_w2v = np.array([
            np.mean([w2v_model.wv[word] for word in text.split() if word in w2v_model.wv]
                    or [np.zeros(100)], axis=0)
            for text in texts
        ])
        X = np.hstack([X, x_w2v])

    try:
        # Взвешивание классов
        class_weights = compute_class_weight(
            'balanced',
            classes=np.unique(labels),
            y=labels
        )
        weights = {i: w for i, w in enumerate(class_weights)}

        model = LinearSVC(
            class_weight=weights,
            max_iter=10000,
            dual=False
        )

        # Разделение на тренировочную и тестовую выборку
        test_size = 0.2 if X.shape[0] > 1000 else 0.1

        x_train, x_test, y_train, y_test = train_test_split(
            X, labels,
            test_size=test_size,
            stratify=labels
        )

        model.fit(x_train, y_train)

        # Сохраняем новую модель
        classifier = CategoryClassifier()
        classifier.save_artifacts(
            model=model,
            vectorizer=vectorizer,
            w2v_model=w2v_model,
            classes=np.unique(labels),
            version=timezone.now().strftime("%Y%m%d%H%M%S")
        )

        logger.info("Model successfully retrained")
        return True

    except Exception as e:
        logger.error(f"Retraining failed: {e}")
        return False

classifier = CategoryClassifier()
