import pytest
from django.contrib.auth import get_user_model

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
