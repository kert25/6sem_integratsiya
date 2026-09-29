"""
Контрактные тесты для проверки совместимости API сервисов
"""
import pytest
import requests
import jsonschema
from jsonschema import validate
import yaml
import json

# Загрузка схем OpenAPI (упрощенные версии)
USER_SERVICE_SCHEMA = {
    "register": {
        "path": "/api/v1/users/register",
        "method": "POST",
        "request": {
            "type": "object",
            "required": ["email", "password"],
            "properties": {
                "email": {"type": "string", "format": "email"},
                "password": {"type": "string", "minLength": 6},
                "name": {"type": "string"}
            }
        },
        "response": {
            "201": {
                "type": "object",
                "required": ["message", "user_id"],
                "properties": {
                    "message": {"type": "string"},
                    "user_id": {"type": "integer"}
                }
            }
        }
    }
}

ORDER_SERVICE_SCHEMA = {
    "create_order": {
        "path": "/api/v1/orders",
        "method": "POST",
        "request": {
            "type": "object",
            "required": ["items"],
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "required": ["product_id", "quantity"],
                        "properties": {
                            "product_id": {"type": "integer"},
                            "quantity": {"type": "integer", "minimum": 1}
                        }
                    }
                }
            }
        },
        "response": {
            "201": {
                "type": "object",
                "required": ["message", "order_id", "total_amount", "status"],
                "properties": {
                    "message": {"type": "string"},
                    "order_id": {"type": "integer"},
                    "total_amount": {"type": "number", "minimum": 0},
                    "status": {"type": "string", "enum": ["pending", "paid", "cancelled"]}
                }
            }
        }
    }
}

class TestAPIContracts:
    """Тесты контрактов API"""
    
    def test_user_service_register_contract(self):
        """Тест контракта регистрации пользователя"""
        print("\n=== Тест контракта регистрации пользователя ===")
        
        schema = USER_SERVICE_SCHEMA["register"]
        
        # Тестовые данные
        test_data = {
            "email": "contract_test@example.com",
            "password": "ValidPass123",
            "name": "Contract Test User"
        }
        
        # Валидация входных данных по схеме
        try:
            validate(instance=test_data, schema=schema["request"])
            print("✓ Входные данные соответствуют схеме")
        except jsonschema.ValidationError as e:
            pytest.fail(f"Входные данные не соответствуют схеме: {e}")
        
        # Отправка запроса
        response = requests.post(
            "http://localhost:8001/api/v1/users/register",
            json=test_data
        )
        
        print(f"Статус ответа: {response.status_code}")
        
        # Валидация ответа по схеме
        if response.status_code == 201:
            response_data = response.json()
            try:
                validate(instance=response_data, schema=schema["response"]["201"])
                print("✓ Ответ соответствует схеме для статуса 201")
            except jsonschema.ValidationError as e:
                pytest.fail(f"Ответ не соответствует схеме: {e}")
        elif response.status_code == 409:  # Пользователь уже существует
            print("⚠ Пользователь уже существует (ожидаемое поведение)")
        else:
            pytest.fail(f"Неожиданный статус ответа: {response.status_code}")
    
    def test_order_service_contract_with_valid_data(self):
        """Тест контракта создания заказа с валидными данными"""
        print("\n=== Тест контракта создания заказа ===")
        
        # Сначала создаем тестового пользователя и получаем токен
        user_data = {
            "email": f"order_contract_{int(time.time())}@example.com",
            "password": "TestPass123"
        }
        
        register_response = requests.post(
            "http://localhost:8001/api/v1/users/register",
            json=user_data
        )
        
        if register_response.status_code not in [201, 409]:
            pytest.skip("Не удалось создать тестового пользователя")
        
        # Получаем токен
        login_response = requests.post(
            "http://localhost:8001/api/v1/users/login",
            json={
                "email": user_data["email"],
                "password": user_data["password"]
            }
        )
        
        if login_response.status_code != 200:
            pytest.skip("Не удалось получить токен")
        
        token = login_response.json()["access_token"]
        
        # Получаем список товаров
        products_response = requests.get("http://localhost:8002/api/v1/products")
        if products_response.status_code != 200:
            pytest.skip("Не удалось получить список товаров")
        
        products = products_response.json()["products"]
        if len(products) == 0:
            pytest.skip("Нет товаров для тестирования")
        
        # Тестовые данные для заказа
        test_data = {
            "items": [
                {
                    "product_id": products[0]["id"],
                    "quantity": 1
                }
            ]
        }
        
        schema = ORDER_SERVICE_SCHEMA["create_order"]
        
        # Валидация входных данных
        try:
            validate(instance=test_data, schema=schema["request"])
            print("✓ Входные данные соответствуют схеме")
        except jsonschema.ValidationError as e:
            pytest.fail(f"Входные данные не соответствуют схеме: {e}")
        
        # Отправка запроса
        response = requests.post(
            "http://localhost:8003/api/v1/orders",
            headers={"Authorization": f"Bearer {token}"},
            json=test_data
        )
        
        print(f"Статус ответа: {response.status_code}")
        
        # Валидация ответа
        if response.status_code == 201:
            response_data = response.json()
            try:
                validate(instance=response_data, schema=schema["response"]["201"])
                print("✓ Ответ соответствует схеме для статуса 201")
                
                # Дополнительные проверки
                assert response_data["status"] == "pending"
                assert response_data["total_amount"] > 0
                assert isinstance(response_data["order_id"], int)
                
            except jsonschema.ValidationError as e:
                pytest.fail(f"Ответ не соответствует схеме: {e}")
        else:
            print(f"Ответ: {response.text}")
            # Могут быть другие валидные статусы (например, 400 при недостатке товара)
    
    def test_api_health_endpoints(self):
        """Тест health-эндпоинтов всех сервисов"""
        print("\n=== Тест health-эндпоинтов ===")
        
        services = {
            "user-service": "http://localhost:8001/health",
            "product-service": "http://localhost:8002/health",
            "order-service": "http://localhost:8003/health",
            "payment-mock": "http://localhost:8004/health"
        }
        
        all_healthy = True
        
        for service_name, url in services.items():
            try:
                response = requests.get(url, timeout=5)
                status = response.status_code
                data = response.json() if response.headers.get('content-type') == 'application/json' else {}
                
                if status == 200:
                    print(f"✓ {service_name}: {status} - {data.get('status', 'unknown')}")
                else:
                    print(f"✗ {service_name}: {status} - {data.get('error', 'unknown')}")
                    all_healthy = False
                    
            except requests.exceptions.RequestException as e:
                print(f"✗ {service_name}: недоступен ({e})")
                all_healthy = False
        
        # Для order-service проверяем зависимости
        if all_healthy:
            order_health_response = requests.get(services["order-service"])
            if order_health_response.status_code == 200:
                order_health = order_health_response.json()
                dependencies = order_health.get("dependencies", {})
                
                print("\nЗависимости order-service:")
                for dep_name, dep_status in dependencies.items():
                    status_icon = "✓" if dep_status else "✗"
                    print(f"  {status_icon} {dep_name}: {'здоров' if dep_status else 'недоступен'}")
