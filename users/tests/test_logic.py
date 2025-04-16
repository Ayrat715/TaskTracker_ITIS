from http import HTTPStatus

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import Client
from django.urls import reverse
from rest_framework.utils import json

User = get_user_model()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "password",
    (["12345678", "12345678"],
     ["testtest", "testtest"],
     ["qwerty123", "qwerty123"],
     ["short", "short"],
     ["alphabetta", "alphagamma"])
)
def test_registration_invalid_password(api_client, password):
    """
    Проверка ошибки регистрации при некорректном пароле.

    :param api_client: клиент для работы с API запросами.
    :param password: содержит вариации тестирования:
    1. Пароль содержит только цифры
    2. Пароль содержит персональные данные
    3. Пароль слишком распространённый
    4. Пароль короткий (менее 8 символов)
    5. Пароли различаются.
    """

    response = api_client.post(
        "/account/registration-user/",
        {
            "email": "test@email.ru",
            "name": "test",
            "password": password[0],
            "password2": password[1],
        }
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_registration_existing_user(api_client, create_user):
    """
    Проверка на недоступность повторной регистрации пользователей.

    :param api_client: клиент для работы с API запросами.
    :param create_user: создание пользователя.
    """

    create_user()
    response = api_client.post(
        "/account/registration-user/",
        {
            "email": "test@test.ru",
            "name": "test",
            "password": "passwordfortest",
            "password2": "passwordfortest",
        }
    )
    assert response.status_code == 400


@pytest.mark.django_db
def test_registration_with_valid_data(api_client):
    """
    Проверка выполнения регистрации с корректными данными.

    :param api_client: клиент для работы с API запросами.
    """

    response = api_client.post(
        "/account/registration-user/",
        {
            "email": "test@email.ru",
            "name": "test",
            "password": "passwordfortest",
            "password2": "passwordfortest",
        }
    )
    assert response.status_code == 201


@pytest.mark.django_db
@pytest.mark.parametrize(
    "login_data",
    (
            ("test@test.ru", "passwordfortest", 200),
            ("invalid@test.ru", "passwordfortest", 400),
            ("test@test.ru", "invalidpassword", 400)
    )
)
def test_login(api_client, create_user, login_data):
    """
    Проверка входа с различными данными.

    :param api_client: клиент для работы с API запросами.
    :param create_user: создание пользователя.
    :param login_data: данные для входа, включающие email, password, ожидаемый
    status_code ответа.
    1. Корректные данные
    2. Некорректная почта
    3. Некорректный пароль.
    """

    email, password, status_code = login_data
    create_user()
    response = api_client.post(
        "/account/login-user/",
        {
            "email": email,
            "password": password,
        }
    )
    assert response.status_code == status_code


@pytest.mark.parametrize(
    'user, result',
    (
            (pytest.lazy_fixture('admin_group_client'), HTTPStatus.CREATED),
            (pytest.lazy_fixture('not_admin_group_client'), HTTPStatus.CREATED),
            (pytest.lazy_fixture('client'), HTTPStatus.FORBIDDEN)
    ),
)
@pytest.mark.parametrize(
    'data',
    ({"users": []},)
)
def test_group_create_availability(user: Client, result: HTTPStatus,
                                   data: dict) -> None:
    """
    Проверка возможности создания группы разными пользователями:
    1. Пользователь, у которого уже существует группа,
    2. Пользователь, у которого нет групп.
    3. Неавторизованный пользователь.

    :param user: Пользователь, от лица которого будут выполняться запросы.
    :param result: Статус-код результата выполнения запроса.
    :param data: Данные POST запроса.
    :return: None.
    """

    url = reverse('users:group-list')
    response = user.post(url, data, content_type='application/json')
    assert response.status_code == result


def test_groups_data_in_group_list(group: Group,
                                   admin_group_client: Client) -> None:
    """
    Проверка данных при получении с GET запроса.

    :param group: Экземпляр созданной группы.
    :param admin_group_client: Пользователь - владелец группы,
    от лица которого отправляется запрос.
    :return: None.
    """

    url = reverse('users:group-list')

    users = []
    for user in group.user_set.all():
        users.append(user.id)
    test_data = {
        'id': group.id,
        'name': group.name,
        'users': users
    }

    response = admin_group_client.get(url)
    response_data = json.loads(response.content.decode('utf-8'))[0]
    assert test_data['id'] == response_data['id']
    assert response_data['name'] == response_data['name']
    assert response_data['users'] == response_data['users']


@pytest.mark.parametrize(
    'user, result',
    ((pytest.lazy_fixture('admin_group_client'), (HTTPStatus.CREATED, 1)),
     (pytest.lazy_fixture('client'), (HTTPStatus.FORBIDDEN, 0)),
     )
)
@pytest.mark.django_db
def test_create_group_availability(form_data: dict, user: Client,
                                   result: HTTPStatus) -> None:
    """
    Проверка создания группы пользователями с разным уровнем доступа:
    1. Авторизованный пользователь.
    2. Неавторизованный пользователь.

    :param form_data: Данные запроса на создание.
    :param user: Пользователь, от лица которого будут выполняться запросы.
    :param result: Значение статус кода и количество
    строк после создания группы.
    """

    url = reverse('users:group-list')

    assert Group.objects.count() == 0

    response = user.post(url, form_data, content_type='application/json')
    response_data = json.loads(response.content.decode('utf-8'))
    print(response_data)

    status_code, count = result

    assert response.status_code == status_code
    assert Group.objects.count() == count

@pytest.mark.django_db
def test_create_group_with_empty_list(form_data: dict,
                                      admin_group_client: Client,
                                      admin_group: User) -> None:
    """
    При создании группы id создающего добавляется в список пользователей группы.

    :param form_data: Данные для создания группы.
    :param admin_group_client: Авторизованный пользователь для создания группы.
    :param admin_group: Экземпляр модели авторизованного пользователя.
    """

    url = reverse('users:group-list')
    response = admin_group_client.post(
        url,
        form_data,
        content_type='application/json'
    )
    id_group = json.loads(response.content.decode('utf-8'))['id']
    group = Group.objects.get(id=id_group)

    assert response.status_code == HTTPStatus.CREATED
    assert admin_group.id in group.user_set.values_list('id', flat=True)

@pytest.mark.parametrize(
    'data',
    (
            {
                'users': None,
            },
            {
                'user': []
            },
            {
                'users': [-1]
            },
            {
                'users': -1
            }
    )
)
@pytest.mark.django_db
def test_incorrect_values_when_creating_a_group(
        admin_group_client: Client, data: dict
) -> None:
    """
    Тестирование на обработку некорректного запроса.

    :param admin_group_client: Авторизованный пользователь.
    :param data: Данные запроса.
    """

    url = reverse('users:group-list')
    response = admin_group_client.post(
        url,
        data,
        content_type='application/json'
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert Group.objects.count() == 0


@pytest.mark.django_db
def test_admin_group_can_edit_group(admin_group_client: Client,
                                    group: Group,
                                    not_admin_group: User) -> None:
    """
    Тест на возможность редактирования состава участников группы пользователем,
    который является участником.

    :param admin_group_client: Авторизованный пользователь, который является
    участником группы.
    :param group: Созданная группа пользователей.
    :param admin_group: Экземпляр пользователя, которого нет в группе.
    """

    url = reverse('users:group-detail', args=(group.id,))

    data = {
        'add_user_id': not_admin_group.id,
    }
    response = admin_group_client.put(
        url,
        data,
        content_type='application/json'
    )
    assert response.status_code == HTTPStatus.OK
    assert not_admin_group.id in group.user_set.values_list('id',
                                                            flat=True)

@pytest.mark.django_db
def test_not_admin_cant_edit_group(not_admin_group_client: Client,
                                   group: Group, new_user: User) -> None:
    """
    Тестирование блокировки доступа к изменению данных у пользователя,
    не состоящего в группе.

    :param not_admin_group_client: Пользователь, не состоящий в группе.
    :param group: Группа.
    :param new_user: Новый пользователь.
    """

    url = reverse('users:group-detail', args=(group.id,))
    data = {
        'add_user_id': new_user.id,
    }
    response = not_admin_group_client.put(
        url,
        data,
        content_type='application/json'
    )
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert new_user.id not in group.user_set.values_list('id', flat=True)


@pytest.mark.django_db
def test_admin_group_can_delete_user(admin_group_client: Client,
                                     group: Group,
                                     new_user: User) -> None:
    """
    Участник группы может удалять других пользователей группы.

    :param admin_group_client: Участник группы.
    :param group: Группа.
    :param new_user: Новый пользователь.
    """

    group.user_set.add(new_user)

    assert new_user.id in group.user_set.values_list('id', flat=True)

    url = reverse('users:group-remove-user', kwargs={
        'pk': group.id,
        'user_id': new_user.id
    })
    response = admin_group_client.delete(url)
    assert response.status_code == HTTPStatus.OK
    assert new_user.id not in group.user_set.values_list('id', flat=True)


@pytest.mark.django_db
def test_not_admin_group_cant_delete_user(not_admin_group_client: Client,
                                          group: Group,
                                          new_user: User) -> None:
    """
    Не участник группы не может удалять других пользователей группы.

    :param not_admin_group_client: Авторизованный пользователь,
    который не состоит в группе.
    :param group: Группа.
    :param new_user: Экземпляр нового пользователя.
    """

    group.user_set.add(new_user)
    url = reverse('users:group-remove-user', kwargs={
        'pk': group.id,
        'user_id': new_user.id
    })
    response = not_admin_group_client.delete(url)
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert new_user.id in group.user_set.values_list('id', flat=True)

@pytest.mark.django_db
def test_admin_group_can_delete_group(admin_group_client: Client,
                                      group: Group) -> None:
    """
    Участник группы может удалить группу.

    :param admin_group_client: Авторизованный пользователь, являющийся
    участником группы.
    :param group: Экземпляр группы.
    """

    assert Group.objects.count() == 1

    url = reverse('users:group-detail', args=(group.id,))
    response = admin_group_client.delete(url)

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert Group.objects.count() == 0

@pytest.mark.django_db
def test_not_admin_group_cant_delete_group(not_admin_group_client: Client,
                                           group: Group) -> None:
    """
    Не участник группы не может удалить группу.

    :param not_admin_group_client: Авторизованный пользователь, не являющийся
    участником группы.
    :param group: Экземпляр группы.
    """

    assert Group.objects.count() == 1

    url = reverse('users:group-detail', args=(group.id,))
    response = not_admin_group_client.delete(url)
    assert response.status_code == HTTPStatus.FORBIDDEN
    assert Group.objects.count() == 1
