import pytest
from django.contrib.auth import get_user_model

from django.urls import reverse
from django.utils.timezone import now, timedelta
from rest_framework import status
from rest_framework.request import Request

from projects.models import Project, Employee
from projects.tests.conftest import group
from users.models import Group

User = get_user_model()


@pytest.mark.parametrize(
    "client_fixture, expected_status",
    [
        ("api_client", status.HTTP_403_FORBIDDEN),
        ("authenticated_client", status.HTTP_400_BAD_REQUEST),
        ("authenticated_client_in_group", status.HTTP_201_CREATED),
    ],
)
@pytest.mark.django_db
def test_create_project(request: Request, client_fixture: User,
                        expected_status: status, group: Group) -> None:
    """
    Параметризованный тест: создание проекта.
    Тестирование проходит с вариантами:
    1. Пользователь: гость,
    2. Пользователь: авторизован, но не в группе,
    3. Пользователь: в группе.

    :param request: Фикстура запроса.
    :param client_fixture: Фикстура клиента.
    :param expected_status: Ожидаемый статус-код ответа.
    :param group: Группа проекта.
    :return: None
    """

    client = request.getfixturevalue(client_fixture)
    url = reverse("projects:index-list")
    data = {
        "name": "New Project",
        "description": "Some description",
        "start_time": now().isoformat(),
        "end_time": (now() + timedelta(days=1)).isoformat(),
        "group": group.id,
    }
    response = client.post(url, data, format="json")
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "client_fixture, expected_status",
    [
        ("another_authenticated_client", status.HTTP_403_FORBIDDEN),
        ("authenticated_client_in_group", status.HTTP_200_OK),
    ],
)
@pytest.mark.django_db
def test_view_project(request: Request, client_fixture: User,
                      expected_status: status, project: Project,
                      employee: Employee) -> None:
    """
    Параметризованный тест: просмотр проекта.
    Варианты тестирования:
    1. Пользователь не в группе,
    2. Пользователь в группе.

    :param request: Фикстура запроса.
    :param client_fixture: Фикстура клиента.
    :param expected_status: Ожидаемый статус-код.
    :param project: Проект.
    :param employee: Сотрудник проекта.
    """

    client = request.getfixturevalue(client_fixture)
    url = reverse("projects:index-detail", kwargs={"pk": project.id})
    response = client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "client_fixture, expected_status",
    [
        ("another_authenticated_client", status.HTTP_403_FORBIDDEN),
        ("authenticated_client_in_group", status.HTTP_200_OK),
    ],
)
@pytest.mark.django_db
def test_edit_project(request: Request, client_fixture: User,
                      expected_status: status, project: Project,
                      employee: Employee) -> None:
    """
    Параметризованный тест: редактирование проекта.
    Варианты тестирования:
    1. Пользователь не в группе,
    2. Пользователь в группе.

    :param request: Фикстура запроса.
    :param client_fixture: Фикстура клиента.
    :param expected_status: Ожидаемый статус-код.
    :param project: Проект.
    :param employee: Сотрудник проекта.
    """

    client = request.getfixturevalue(client_fixture)
    url = reverse("projects:index-detail", kwargs={"pk": project.id})
    data = {
        "name": "Updated Project Name",
        "description": project.description,
        "start_time": project.start_time.isoformat(),
        "end_time": project.end_time.isoformat(),
        "group": project.group.id,
    }
    response = client.patch(url, data, format="json")
    assert response.status_code == expected_status
    if expected_status == status.HTTP_200_OK:
        project.refresh_from_db()
        assert project.name == "Updated Project Name"


@pytest.mark.parametrize(
    "client_fixture, expected_status",
    [
        ("another_authenticated_client", status.HTTP_403_FORBIDDEN),
        # Пользователь не в группе
        ("authenticated_client_in_group", status.HTTP_204_NO_CONTENT),
        # Пользователь в группе
    ],
)
@pytest.mark.django_db
def test_delete_project(request: Request, client_fixture: User,
                        expected_status: status, project: Project,
                        employee: Employee) -> None:
    """
    Параметризованный тест: удаление проекта.
    Варианты тестирования:
    1. Пользователь не в группе,
    2. Пользователь в группе.

    :param request: Фикстура запроса.
    :param client_fixture: Фикстура клиента.
    :param expected_status: Ожидаемый статус-код.
    :param project: Проект.
    :param employee: Сотрудник проекта.
    """

    client = request.getfixturevalue(client_fixture)
    url = reverse("projects:index-detail", kwargs={"pk": project.id})
    response = client.delete(url)
    assert response.status_code == expected_status
    if expected_status == status.HTTP_204_NO_CONTENT:
        assert Project.objects.count() == 0
