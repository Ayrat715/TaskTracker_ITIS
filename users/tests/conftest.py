import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test.client import Client

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

@pytest.fixture
def admin_group(django_user_model):
    return django_user_model.objects.create(email='admin@test.ru', name='Admin')

@pytest.fixture
def not_admin_group(django_user_model):
    return django_user_model.objects.create(
        email='notadmin@test.ru',
        name='Not Admin'
    )

@pytest.fixture
def admin_group_client(admin_group):
    client = Client()
    client.force_login(admin_group)
    return client

@pytest.fixture
def not_admin_group_client(not_admin_group):
    client = Client()
    client.force_login(not_admin_group)
    return client

@pytest.fixture
def group(admin_group):
    group = Group.objects.create(name='Group')
    group.user_set.add(admin_group)
    return group

@pytest.fixture
def form_data():
    return {
        'users': []
    }

@pytest.fixture
def new_user():
    new_user = get_user_model().objects.create(
        email='testuser@test.ru',
        name='Not Admin'
    )
    return new_user
