# -*- coding: utf-8 -*-
"""
Фикстуры pytest для тестов API
"""
import pytest
from faker import Faker

from api.client import APIClient, TasksAPI, AuthAPI, ProductsAPI
from api.schemas import Task, AuthResponse
from utils.logger import setup_logging
from utils.helpers import wait_for_server

BASE_URL = "http://localhost:5000"


@pytest.fixture(scope="session", autouse=True)
def _logging():
    """Инициализация логирования на всю тестовую сессию"""
    setup_logging()


@pytest.fixture(scope="session")
def faker():
    """Генератор тестовых данных"""
    return Faker('ru_RU')


@pytest.fixture(scope="session")
def api_client():
    """Клиент для работы с API (с ожиданием готовности сервера)"""
    wait_for_server(BASE_URL)
    client = APIClient(base_url=BASE_URL)
    yield client
    client.session.close()


@pytest.fixture(autouse=True)
def reset_data(api_client):
    """Сброс данных перед каждым тестом (POST /api/v1/reset).

    Обеспечивает изолированность и идемпотентность тестов:
    каждый тест работает с предсказуемым начальным состоянием.
    """
    response = api_client.post('/api/v1/reset')
    assert response.status_code == 200
    yield


@pytest.fixture
def tasks_api(api_client):
    """API для работы с задачами"""
    return TasksAPI(api_client)


@pytest.fixture
def auth_api(api_client):
    """API для аутентификации"""
    return AuthAPI(api_client)


@pytest.fixture
def products_api(api_client):
    """API для работы с товарами"""
    return ProductsAPI(api_client)


@pytest.fixture
def auth_token(auth_api):
    """Получение токена аутентификации"""
    response = auth_api.login("student@university.ru", "password123")
    auth_data = AuthResponse.model_validate(response.json())
    return auth_data.token


@pytest.fixture
def authenticated_client(api_client, auth_token):
    """Клиент с установленным токеном аутентификации"""
    api_client.set_auth_token(auth_token)
    yield api_client
    # Сбрасываем токен после теста
    api_client.token = None
    api_client.session.headers.pop('Authorization', None)


@pytest.fixture
def test_task(tasks_api, faker):
    """Создание тестовой задачи и её удаление после теста"""
    title = faker.sentence(nb_words=4)
    response = tasks_api.create_task(title=title)
    task_data = Task.model_validate(response.json())

    yield task_data

    # Удаляем задачу после теста (очистка)
    try:
        tasks_api.delete_task(task_data.id)
    except Exception:
        pass  # Игнорируем ошибки при удалении


@pytest.fixture
def test_user(auth_api, faker):
    """Создание тестового пользователя"""
    email = faker.email()
    password = faker.password()
    name = faker.name()

    response = auth_api.register(email, password, name)
    user_id = response.json()['userId']

    return {
        'email': email,
        'password': password,
        'name': name,
        'id': user_id
    }
