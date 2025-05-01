from django.core.management.base import BaseCommand
from keybert import KeyBERT
from django.db import transaction
from yake import KeywordExtractor
from tasks.ml_category import CategoryClassifier, keyword_matcher
from tasks.models import TaskCategory, Task


class Command(BaseCommand):
    help = 'Автоматически присваивает (или создаёт) категории для всех задач без категории'

    def handle(self, *args, **options):
        classifier = CategoryClassifier()
        extractor_yake = KeywordExtractor(lan="ru", n=2, top=3)
        kw_model = KeyBERT(model='all-MiniLM-L6-v2')
        count = 0

        for task in Task.objects.filter(category__isnull=True):
            cat = keyword_matcher(task, TaskCategory.objects.all())
            if cat:
                task.category = cat
                task.save(update_fields=['category'])
                self.stdout.write(f'✅ (keyword) {task.name} → {cat.name}')
                count += 1
                continue

            pred = classifier.predict(task)
            if pred:
                cat_obj, created = TaskCategory.objects.get_or_create(name=pred)
                task.category = cat_obj
                task.save(update_fields=['category'])
                self.stdout.write(f'✅ (ml)      {task.name} → {pred} {"(new)" if created else ""}')
                count += 1
                continue

            text = (task.name + " " + (task.description or "")).strip()
            kw = extractor_yake.extract_keywords(text)
            if kw:
                new_name = kw[0][0]
            else:
                kb = kw_model.extract_keywords(text, keyphrase_ngram_range=(1,2), top_n=1)
                new_name = kb[0][0] if kb else task.name[:50]

            with transaction.atomic():
                new_cat, created = TaskCategory.objects.get_or_create(
                    name=new_name,
                    defaults={'keywords': new_name}
                )
                task.category = new_cat
                task.save(update_fields=['category'])
            self.stdout.write(f'🆕 (newcat)  {task.name} → {new_name}')
            count += 1

        self.stdout.write(self.style.SUCCESS(f'Готово, обновлено {count} задач.'))
