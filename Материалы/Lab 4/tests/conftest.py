"""
Фикстуры pytest для тестов API
"""
import pytest
from faker import Faker
from api.client import APIClient, TasksAPI, AuthAPI
from api.schemas import Task, AuthResponse



@pytest.fixture(scope="session")
def faker():
    """Генератор тестовых данных"""
    return Faker('ru_RU')


@pytest.fixture(scope="session")
def api_client():
    """Клиент для работы с API"""
    client = APIClient(base_url="http://localhost:5000")
    yield client
    client.session.close()


@pytest.fixture
def tasks_api(api_client):
    """API для работы с задачами"""
    return TasksAPI(api_client)


@pytest.fixture
def auth_api(api_client):
    """API для аутентификации"""
    return AuthAPI(api_client)


@pytest.fixture
def auth_token(auth_api):
    """Получение токена аутентификации"""
    response = auth_api.login("student@university.ru", "password123")
    auth_data = AuthResponse.parse_obj(response.json())
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
    # Создаем задачу
    title = faker.sentence(nb_words=4)
    response = tasks_api.create_task(title=title)
    task_data = Task.parse_obj(response.json())
    
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
