# -*- coding: utf-8 -*-
"""
Клиент для работы с тестовым API (ЛР4).

Обертка над requests: управление сессией, заголовками и аутентификацией,
логирование запросов и ответов. Методы возвращают объект requests.Response,
статусы (в том числе 400/401/404/409) проверяются в самих тестах.
"""
import logging
from typing import Optional, Dict
import requests
from requests.exceptions import RequestException

logger = logging.getLogger(__name__)


class APIClient:
    """Клиент для работы с REST API"""

    def __init__(self, base_url: str, timeout: int = 10):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        self.token: Optional[str] = None

        # Настройка логирования через hook на все ответы сессии
        self.session.hooks['response'].append(self._log_response)

    def _log_response(self, response: requests.Response, *args, **kwargs):
        """Логирование HTTP-запросов и ответов"""
        logger.info(f"Request: {response.request.method} {response.request.url}")
        logger.info(f"Request body: {response.request.body}")
        logger.info(f"Response status: {response.status_code}")
        logger.info(f"Response body: {response.text[:500]}...")
        return response

    def set_auth_token(self, token: str):
        """Установка токена аутентификации"""
        self.token = token
        self.session.headers.update({'Authorization': f'Bearer {token}'})

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Выполнение HTTP-запроса"""
        url = f"{self.base_url}{endpoint}"

        # Установка таймаута по умолчанию
        if 'timeout' not in kwargs:
            kwargs['timeout'] = self.timeout

        try:
            response = self.session.request(method, url, **kwargs)
        except RequestException as e:
            logger.error(f"Request failed: {e}")
            raise

        # HTTP-ошибки не превращаем в исключения: статус проверяет тест
        if response.status_code >= 400:
            logger.warning(
                f"HTTP {response.status_code} for {method} {endpoint}: "
                f"{response.text[:300]}"
            )
        return response

    def get(self, endpoint: str, params: Optional[Dict] = None, **kwargs) -> requests.Response:
        return self._request('GET', endpoint, params=params, **kwargs)

    def post(self, endpoint: str, json: Optional[Dict] = None, **kwargs) -> requests.Response:
        return self._request('POST', endpoint, json=json, **kwargs)

    def put(self, endpoint: str, json: Optional[Dict] = None, **kwargs) -> requests.Response:
        return self._request('PUT', endpoint, json=json, **kwargs)

    def patch(self, endpoint: str, json: Optional[Dict] = None, **kwargs) -> requests.Response:
        return self._request('PATCH', endpoint, json=json, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        return self._request('DELETE', endpoint, **kwargs)


class TasksAPI:
    """Клиент для работы с API задач"""

    def __init__(self, client: APIClient):
        self.client = client

    def get_all_tasks(self, completed: Optional[bool] = None, user_id: Optional[int] = None):
        params = {}
        if completed is not None:
            params['completed'] = str(completed).lower()
        if user_id is not None:
            params['userId'] = user_id
        return self.client.get('/api/v1/tasks', params=params)

    def create_task(self, title: Optional[str] = None, completed: bool = False, user_id: int = 1):
        # title=None означает "пустое тело запроса" (проверка негативного сценария)
        if title is None:
            return self.client.post('/api/v1/tasks', json={})
        data = {
            'title': title,
            'completed': completed,
            'userId': user_id
        }
        return self.client.post('/api/v1/tasks', json=data)

    def get_task(self, task_id: int):
        return self.client.get(f'/api/v1/tasks/{task_id}')

    def update_task(self, task_id: int, title: str, completed: bool):
        data = {
            'title': title,
            'completed': completed
        }
        return self.client.put(f'/api/v1/tasks/{task_id}', json=data)

    def delete_task(self, task_id: int):
        return self.client.delete(f'/api/v1/tasks/{task_id}')


class AuthAPI:
    """Клиент для работы с API аутентификации"""

    def __init__(self, client: APIClient):
        self.client = client

    def login(self, email: str, password: str):
        data = {
            'email': email,
            'password': password
        }
        return self.client.post('/api/v1/auth/login', json=data)

    def register(self, email: str, password: str, name: str = ""):
        data = {
            'email': email,
            'password': password,
            'name': name
        }
        return self.client.post('/api/v1/auth/register', json=data)

    def logout(self):
        return self.client.post('/api/v1/auth/logout')

    def get_current_user(self):
        return self.client.get('/api/v1/users/me')


class ProductsAPI:
    """Клиент для работы с API товаров"""

    def __init__(self, client: APIClient):
        self.client = client

    def get_products(self, category: Optional[str] = None,
                     min_price: Optional[float] = None,
                     max_price: Optional[float] = None,
                     in_stock: Optional[bool] = None):
        params = {}
        if category is not None:
            params['category'] = category
        if min_price is not None:
            params['minPrice'] = min_price
        if max_price is not None:
            params['maxPrice'] = max_price
        if in_stock is not None:
            params['inStock'] = str(in_stock).lower()
        return self.client.get('/api/v1/products', params=params)

    def get_product(self, product_id: int):
        return self.client.get(f'/api/v1/products/{product_id}')
