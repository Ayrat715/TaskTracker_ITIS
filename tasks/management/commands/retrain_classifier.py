from django.core.management.base import BaseCommand
from tasks.ml_category import CategoryClassifier


class Command(BaseCommand):
    help = 'Переобучить классификатор категорий на текущих данных'

    def handle(self, *args, **options):
        classifier = CategoryClassifier()
        classifier.train()
        self.stdout.write(self.style.SUCCESS('Классификатор успешно переобучен'))
