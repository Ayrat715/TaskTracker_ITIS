import pytest
from django.test import Client

from django.urls import reverse
from http import HTTPStatus


@pytest.mark.parametrize(
    'user, result',
    (
            (pytest.lazy_fixture('admin_group_client'), HTTPStatus.OK),
            (pytest.lazy_fixture('not_admin_group_client'), HTTPStatus.OK),
            (pytest.lazy_fixture('client'), HTTPStatus.FORBIDDEN)
    ),
)
def test_user_list_availability(user: Client, result: HTTPStatus) -> None:
    """
    Тест на доступность страницы с результатами поиска.

    :param user: Пользователь, от лица которого будут выполняться запросы.
    :param result: Статус-код результата выполнения запроса.
    :return: None
    """

    url = reverse('users:user_list') + '?email='
    response = user.get(url)
    assert response.status_code == result


@pytest.mark.parametrize(
    'user, result',
    (
            (pytest.lazy_fixture('admin_group_client'), HTTPStatus.OK),
            (pytest.lazy_fixture('not_admin_group_client'), HTTPStatus.OK),
            (pytest.lazy_fixture('client'), HTTPStatus.FORBIDDEN)
    ),
)
def test_group_list_availability(user: Client, result: HTTPStatus) -> None:
    """
    Проверка на доступность страницы со списком групп.

    :param user: Пользователь, от лица которого будут выполняться запросы.
    :param result: Статус-код результата выполнения запроса.
    :return: None
    """

    url = reverse('users:group-list')
    response = user.get(url)
    assert response.status_code == result
