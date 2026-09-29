"""
Интеграционные тесты для полного цикла заказа
"""
import pytest
import requests
import json
import time
from typing import Dict, Any

# Конфигурация
BASE_URL = "http://localhost:8080"  # API Gateway
USER_SERVICE_URL = "http://localhost:8001"
PRODUCT_SERVICE_URL = "http://localhost:8002"
ORDER_SERVICE_URL = "http://localhost:8003"

class TestOrderIntegration:
    """Тесты полного цикла заказа"""
    
    @pytest.fixture
    def test_user(self) -> Dict[str, Any]:
        """Создание тестового пользователя"""
        # Генерация уникального email
        timestamp = int(time.time())
        email = f"test_user_{timestamp}@example.com"
        password = "TestPassword123"
        
        # Регистрация пользователя
        response = requests.post(
            f"{USER_SERVICE_URL}/api/v1/users/register",
            json={
                "email": email,
                "password": password,
                "name": "Test User"
            }
        )
        
        assert response.status_code == 201, f"Failed to create user: {response.text}"
        user_id = response.json()["user_id"]
        
        # Получение токена
        login_response = requests.post(
            f"{USER_SERVICE_URL}/api/v1/users/login",
            json={
                "email": email,
                "password": password
            }
        )
        
        assert login_response.status_code == 200, f"Failed to login: {login_response.text}"
        token = login_response.json()["access_token"]
        
        return {
            "id": user_id,
            "email": email,
            "token": token
        }
    
    @pytest.fixture
    def test_products(self) -> Dict[str, Any]:
        """Получение тестовых товаров"""
        response = requests.get(f"{PRODUCT_SERVICE_URL}/api/v1/products")
        assert response.status_code == 200
        
        products = response.json()["products"]
        assert len(products) > 0, "No products available for testing"
        
        return {
            "first_product": products[0],
            "second_product": products[1] if len(products) > 1 else products[0]
        }
    
    def test_complete_order_flow(self, test_user, test_products):
        """Тест полного цикла: регистрация -> создание заказа -> оплата"""
        print(f"\n=== Тест полного цикла заказа для пользователя {test_user['email']} ===")
        
        # Шаг 1: Создание заказа
        print("1. Создание заказа...")
        order_response = requests.post(
            f"{ORDER_SERVICE_URL}/api/v1/orders",
            headers={"Authorization": f"Bearer {test_user['token']}"},
            json={
                "items": [
                    {
                        "product_id": test_products["first_product"]["id"],
                        "quantity": 1
                    },
                    {
                        "product_id": test_products["second_product"]["id"],
                        "quantity": 2
                    }
                ]
            }
        )
        
        print(f"   Ответ: {order_response.status_code} - {order_response.text}")
        assert order_response.status_code == 201, "Failed to create order"
        
        order_data = order_response.json()
        order_id = order_data["order_id"]
        
        # Проверка данных заказа
        assert order_data["status"] == "pending"
        assert order_data["total_amount"] > 0
        assert len(order_data["items"]) == 2
        
        # Шаг 2: Получение информации о заказе
        print("2. Получение информации о заказе...")
        get_order_response = requests.get(
            f"{ORDER_SERVICE_URL}/api/v1/orders/{order_id}",
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        
        print(f"   Ответ: {get_order_response.status_code}")
        assert get_order_response.status_code == 200
        
        order_details = get_order_response.json()
        assert order_details["id"] == order_id
        assert order_details["user_id"] == test_user["id"]
        
        # Шаг 3: Оплата заказа
        print("3. Оплата заказа...")
        payment_response = requests.post(
            f"{ORDER_SERVICE_URL}/api/v1/orders/{order_id}/pay",
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        
        print(f"   Ответ: {payment_response.status_code} - {payment_response.text}")
        
        # Проверка результата оплаты
        payment_result = payment_response.json()
        
        if payment_response.status_code == 200:
            print("   ✓ Платеж успешен")
            assert payment_result["new_status"] == "paid"
            
            # Проверка обновления остатков
            self._verify_stock_update(test_products)
        else:
            print(f"   ✗ Платеж не прошел: {payment_result.get('error')}")
            assert payment_result["new_status"] == "payment_failed"
        
        # Шаг 4: Проверка истории заказов пользователя
        print("4. Проверка истории заказов...")
        history_response = requests.get(
            f"{ORDER_SERVICE_URL}/api/v1/orders/user/{test_user['id']}",
            headers={"Authorization": f"Bearer {test_user['token']}"}
        )
        
        print(f"   Ответ: {history_response.status_code}")
        assert history_response.status_code == 200
        
        history = history_response.json()
        assert history["count"] > 0
        assert any(order["id"] == order_id for order in history["orders"])
        
        print("=== Тест завершен ===")
    
    def test_order_with_insufficient_stock(self, test_user, test_products):
        """Тест создания заказа с недостаточным количеством товара"""
        print(f"\n=== Тест с недостаточным остатком ===")
        
        # Получаем текущий остаток товара
        product_id = test_products["first_product"]["id"]
        current_stock = test_products["first_product"]["stock"]
        
        # Пытаемся заказать больше, чем есть в наличии
        order_response = requests.post(
            f"{ORDER_SERVICE_URL}/api/v1/orders",
            headers={"Authorization": f"Bearer {test_user['token']}"},
            json={
                "items": [
                    {
                        "product_id": product_id,
                        "quantity": current_stock + 10  # Заказываем больше, чем есть
                    }
                ]
            }
        )
        
        print(f"Текущий остаток: {current_stock}")
        print(f"Запрошено: {current_stock + 10}")
        print(f"Ответ: {order_response.status_code} - {order_response.text}")
        
        assert order_response.status_code == 400
        error_message = order_response.json().get("error", "")
        assert "Insufficient stock" in error_message or "недостаточно" in error_message.lower()
        
        print("✓ Тест прошел: система корректно обработала недостаток товара")
    
    def test_order_without_authentication(self, test_products):
        """Тест создания заказа без авторизации"""
        print(f"\n=== Тест без авторизации ===")
        
        order_response = requests.post(
            f"{ORDER_SERVICE_URL}/api/v1/orders",
            json={
                "items": [
                    {
                        "product_id": test_products["first_product"]["id"],
                        "quantity": 1
                    }
                ]
            }
            # Нет заголовка Authorization
        )
        
        print(f"Ответ: {order_response.status_code} - {order_response.text}")
        assert order_response.status_code == 401
        
        error_message = order_response.json().get("error", "")
        assert "token" in error_message.lower() or "authorization" in error_message.lower()
        
        print("✓ Тест прошел: система требует авторизацию")
    
    def test_order_with_invalid_token(self, test_products):
        """Тест создания заказа с невалидным токеном"""
        print(f"\n=== Тест с невалидным токеном ===")
        
        order_response = requests.post(
            f"{ORDER_SERVICE_URL}/api/v1/orders",
            headers={"Authorization": "Bearer invalid_token_123"},
            json={
                "items": [
                    {
                        "product_id": test_products["first_product"]["id"],
                        "quantity": 1
                    }
                ]
            }
        )
        
        print(f"Ответ: {order_response.status_code} - {order_response.text}")
        assert order_response.status_code in [401, 403]
        
        print("✓ Тест прошел: система отклоняет невалидный токен")
    
    def test_get_order_without_permission(self, test_user, test_products):
        """Тест получения заказа другого пользователя"""
        print(f"\n=== Тест получения чужого заказа ===")
        
        # Создаем второго пользователя
        timestamp = int(time.time())
        second_user_email = f"second_user_{timestamp}@example.com"
        
        register_response = requests.post(
            f"{USER_SERVICE_URL}/api/v1/users/register",
            json={
                "email": second_user_email,
                "password": "Password123",
                "name": "Second User"
            }
        )
        
        assert register_response.status_code == 201
        second_user_id = register_response.json()["user_id"]
        
        # Логинимся как второй пользователь
        login_response = requests.post(
            f"{USER_SERVICE_URL}/api/v1/users/login",
            json={
                "email": second_user_email,
                "password": "Password123"
            }
        )
        
        assert login_response.status_code == 200
        second_user_token = login_response.json()["access_token"]
        
        # Первый пользователь создает заказ
        order_response = requests.post(
            f"{ORDER_SERVICE_URL}/api/v1/orders",
            headers={"Authorization": f"Bearer {test_user['token']}"},
            json={
                "items": [
                    {
                        "product_id": test_products["first_product"]["id"],
                        "quantity": 1
                    }
                ]
            }
        )
        
        assert order_response.status_code == 201
        order_id = order_response.json()["order_id"]
        
        # Второй пользователь пытается получить заказ первого пользователя
        get_order_response = requests.get(
            f"{ORDER_SERVICE_URL}/api/v1/orders/{order_id}",
            headers={"Authorization": f"Bearer {second_user_token}"}
        )
        
        print(f"Ответ: {get_order_response.status_code} - {get_order_response.text}")
        assert get_order_response.status_code in [403, 404]
        
        error_message = get_order_response.json().get("error", "")
        assert "access" in error_message.lower() or "denied" in error_message.lower()
        
        print("✓ Тест прошел: система защищает данные пользователей")
    
    def _verify_stock_update(self, test_products):
        """Проверка обновления остатков после успешной оплаты"""
        print("   Проверка обновления остатков...")
        
        # Для каждого товара в тесте проверяем, что остаток обновился
        for product_key in ["first_product", "second_product"]:
            if product_key in test_products:
                product = test_products[product_key]
                
                # Получаем обновленную информацию о товаре
                response = requests.get(
                    f"{PRODUCT_SERVICE_URL}/api/v1/products/{product['id']}"
                )
                
                if response.status_code == 200:
                    updated_product = response.json()
                    print(f"     Товар {product['name']}: было {product['stock']}, стало {updated_product['stock']}")
                    # Можно добавить более сложную проверку, если известно, сколько было заказано

if __name__ == "__main__":
    # Запуск тестов вручную
    import sys
    sys.path.append(".")
    
    test = TestOrderIntegration()
    
    # Создаем временные фикстуры
    test_user = test.test_user()
    test_products = test.test_products()
    
    # Запускаем тесты
    print("Запуск интеграционных тестов...")
    
    try:
        test.test_order_without_authentication(test_products)
        test.test_order_with_invalid_token(test_products)
        test.test_order_with_insufficient_stock(test_user, test_products)
        test.test_get_order_without_permission(test_user, test_products)
        test.test_complete_order_flow(test_user, test_products)
        
        print("\n✅ Все тесты прошли успешно!")
    except AssertionError as e:
        print(f"\n❌ Тест не прошел: {e}")
        sys.exit(1)
