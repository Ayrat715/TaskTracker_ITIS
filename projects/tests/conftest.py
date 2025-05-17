import pytest
from django.contrib.auth import get_user_model

from django.utils.timezone import now, timedelta
from projects.models import Project, Employee, ProjectRole
from rest_framework.test import APIClient
from users.models import Group

User = get_user_model()


@pytest.fixture
def api_client() -> APIClient:
    """Тестирование через API DRF клиента."""

    return APIClient()


@pytest.fixture
def user() -> User:
    """Создание пользователя."""

    return User.objects.create_user(name="user1", email="user1@test.ru",
                                    password="password123")


@pytest.fixture
def another_user() -> User:
    """Создание второго пользователя."""

    return User.objects.create_user(name="user2", email="user2@test.ru",
                                    password="password123")


@pytest.fixture
def group() -> Group:
    """Создание группы."""

    return Group.objects.create(name="Test Group")


@pytest.fixture
def user_in_group(user: User, group: Group) -> User:
    """
    Добавление пользователя в группу.

    :param user: Пользователь.
    :param group: Группа для добавления.
    :return: Пользователь, добавленный в группу.
    """

    group.user_set.add(user)
    return user


@pytest.fixture
def project(group: Group) -> Project:
    """
    Создание проекта.

    :param group: Группа, которая будет прикреплена к проекту.
    :return: Project
    """

    return Project.objects.create(
        name="Test Project",
        description="Test Description",
        start_time=now(),
        end_time=now() + timedelta(days=1),
        group=group
    )


@pytest.fixture
def employee(project: Project, user_in_group: User) -> Employee:
    """
    Создание экземпляра сотрудника проекта.

    :param project: Экземпляр проекта.
    :param user_in_group: Пользователь, находящийся в группе проекта.
    :return: Employee сотрудник проекта.
    """

    employee = Employee.objects.create(
        user=user_in_group,
        project=project,
        role=ProjectRole.objects.create(name="Test Role", project=project)
    )

    return employee


@pytest.fixture
def authenticated_client(api_client: APIClient, user: User) -> APIClient:
    """
    Аутентификация пользователя.

    :param api_client: API Client из DRF.
    :param user: Пользователь, который будет аутентифицирован.
    :return: APIClient
    """

    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def another_authenticated_client(api_client: APIClient,
                                 another_user: User) -> APIClient:
    """
    Аутентификация второго пользователя.

    :param api_client: API Client из DRF.
    :param another_user: Пользователь, который будет аутентифицирован.
    :return: APIClient
    """

    api_client.force_authenticate(user=another_user)
    return api_client


@pytest.fixture
def authenticated_client_in_group(api_client: APIClient,
                                  user_in_group: User) -> APIClient:
    """
    Аутентификация пользователя в группе.

    :param api_client: API Client из DRF.
    :param user_in_group: Пользователь из группы.
    :return: APIClient
    """

    api_client.force_authenticate(user=user_in_group)
    return api_client
