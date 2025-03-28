import pytest
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient

User = get_user_model()

@pytest.fixture
def api_client():
    """Тестирование через API DRF клиента."""

    return APIClient()

@pytest.fixture
def create_user():
    """Создание пользователя."""

    def _create_user(name="test", email="test@test.ru", password="passwordfortest"):
        user = User.objects.create(name=name, email=email)
        user.set_password(password)
        user.save()
        return user
    return _create_user
