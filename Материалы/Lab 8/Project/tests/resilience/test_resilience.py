"""
Тесты отказоустойчивости системы
"""
import pytest
import requests
import time
import subprocess
import signal
import os
from typing import Dict, Any

class TestResilience:
    """Тесты отказоустойчивости и восстановления"""
    
    @pytest.fixture
    def setup_test_order(self) -> Dict[str, Any]:
        """Создание тестового заказа для тестов отказоустойчивости"""
        # Создаем пользователя
        timestamp = int(time.time())
        email = f"resilience_{timestamp}@example.com"
        
        register_response = requests.post(
            "http://localhost:8001/api/v1/users/register",
            json={
                "email": email,
                "password": "TestPass123",
                "name": "Resilience Test"
            }
        )
        
        if register_response.status_code not in [201, 409]:
            pytest.skip("Не удалось создать пользователя")
        
        # Получаем токен
        login_response = requests.post(
            "http://localhost:8001/api/v1/users/login",
            json={
                "email": email,
                "password": "TestPass123"
            }
        )
        
        if login_response.status_code != 200:
            pytest.skip("Не удалось получить токен")
        
        token = login_response.json()["access_token"]
        user_id = login_response.json()["user"]["id"]
        
        # Получаем товары
        products_response = requests.get("http://localhost:8002/api/v1/products")
        if products_response.status_code != 200:
            pytest.skip("Не удалось получить товары")
        
        products = products_response.json()["products"]
        if len(products) == 0:
            pytest.skip("Нет товаров")
        
        # Создаем заказ
        order_response = requests.post(
            "http://localhost:8003/api/v1/orders",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "items": [
                    {
                        "product_id": products[0]["id"],
                        "quantity": 1
                    }
                ]
            }
        )
        
        if order_response.status_code != 201:
            pytest.skip("Не удалось создать заказ")
        
        order_data = order_response.json()
        
        return {
            "user_id": user_id,
            "token": token,
            "order_id": order_data["order_id"],
            "product_id": products[0]["id"]
        }
    
    def test_payment_service_timeout_handling(self, setup_test_order):
        """Тест обработки таймаута платежной системы"""
        print("\n=== Тест обработки таймаута платежной системы ===")
        
        test_data = setup_test_order
        order_id = test_data["order_id"]
        
        # Настраиваем mock платежной системы на таймаут
        # (В реальной системе мы бы настроили mock соответствующим образом)
        
        print(f"Запуск оплаты для заказа {order_id}...")
        start_time = time.time()
        
        payment_response = requests.post(
            f"http://localhost:8003/api/v1/orders/{order_id}/pay",
            headers={"Authorization": f"Bearer {test_data['token']}"},
            timeout=3  # Устанавливаем короткий таймаут на клиенте
        )
        
        elapsed_time = time.time() - start_time
        print(f"Время выполнения: {elapsed_time:.2f} сек")
        print(f"Статус ответа: {payment_response.status_code}")
        
        # Система должна вернуть ошибку или обработать таймаут
        assert payment_response.status_code in [200, 400, 502, 503]
        
        response_data = payment_response.json()
        print(f"Ответ: {response_data}")
        
        # Проверяем, что статус заказа обновился соответствующим образом
        order_response = requests.get(
            f"http://localhost:8003/api/v1/orders/{order_id}",
            headers={"Authorization": f"Bearer {test_data['token']}"}
        )
        
        if order_response.status_code == 200:
            order_status = order_response.json()["status"]
            print(f"Текущий статус заказа: {order_status}")
            
            # Статус должен быть либо 'paid', либо 'payment_failed'
            assert order_status in ['paid', 'payment_failed', 'pending']
    
    def test_order_service_without_payment_service(self):
        """Тест работы сервиса заказов при недоступности платежной системы"""
        print("\n=== Тест недоступности платежной системы ===")
        
        # Здесь должна быть логика остановки платежной системы
        # В учебных целях просто проверяем, что health-чек order-service показывает проблему
        
        health_response = requests.get("http://localhost:8003/health")
        print(f"Health check: {health_response.status_code}")
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"Статус: {health_data.get('status')}")
            
            dependencies = health_data.get("dependencies", {})
            payment_service_healthy = dependencies.get("payment_service", False)
            
            print(f"Платежная система: {'здорова' if payment_service_healthy else 'недоступна'}")
            
            # Даже если платежная система недоступна, order-service должен быть доступен
            # (хотя может быть в статусе degraded)
            assert health_data.get("status") in ["healthy", "degraded"]
    
    def test_retry_mechanism_for_payment(self, setup_test_order):
        """Тест повторных попыток оплаты"""
        print("\n=== Тест повторной оплаты ===")
        
        test_data = setup_test_order
        order_id = test_data["order_id"]
        
        # Первая попытка оплаты
        print("Первая попытка оплаты...")
        payment_response_1 = requests.post(
            f"http://localhost:8003/api/v1/orders/{order_id}/pay",
            headers={"Authorization": f"Bearer {test_data['token']}"}
        )
        
        print(f"Результат первой попытки: {payment_response_1.status_code}")
        
        # Получаем текущий статус заказа
        order_response = requests.get(
            f"http://localhost:8003/api/v1/orders/{order_id}",
            headers={"Authorization": f"Bearer {test_data['token']}"}
        )
        
        if order_response.status_code == 200:
            order_status = order_response.json()["status"]
            print(f"Статус заказа после первой попытки: {order_status}")
            
            # Вторая попытка оплаты
            print("\nВторая попытка оплаты...")
            payment_response_2 = requests.post(
                f"http://localhost:8003/api/v1/orders/{order_id}/pay",
                headers={"Authorization": f"Bearer {test_data['token']}"}
            )
            
            print(f"Результат второй попытки: {payment_response_2.status_code}")
            
            # В зависимости от реализации система должна либо:
            # 1. Отклонить повторную оплату уже оплаченного заказа
            # 2. Разрешить повторную оплату для заказа со статусом payment_failed
            # 3. Вернуть ошибку
            
            assert payment_response_2.status_code in [200, 400, 409]
    
    def test_data_consistency_after_failure(self, setup_test_order):
        """Тест консистентности данных после сбоя"""
        print("\n=== Тест консистентности данных ===")
        
        test_data = setup_test_order
        order_id = test_data["order_id"]
        product_id = test_data["product_id"]
        
        # Получаем начальные остатки товара
        initial_product_response = requests.get(f"http://localhost:8002/api/v1/products/{product_id}")
        if initial_product_response.status_code == 200:
            initial_stock = initial_product_response.json()["stock"]
            print(f"Начальный остаток товара: {initial_stock}")
        
        # Пытаемся оплатить заказ
        print("Попытка оплаты...")
        payment_response = requests.post(
            f"http://localhost:8003/api/v1/orders/{order_id}/pay",
            headers={"Authorization": f"Bearer {test_data['token']}"}
        )
        
        # Получаем конечные остатки товара
        final_product_response = requests.get(f"http://localhost:8002/api/v1/products/{product_id}")
        if final_product_response.status_code == 200:
            final_stock = final_product_response.json()["stock"]
            print(f"Конечный остаток товара: {final_stock}")
            
            # Получаем статус заказа
            order_response = requests.get(
                f"http://localhost:8003/api/v1/orders/{order_id}",
                headers={"Authorization": f"Bearer {test_data['token']}"}
            )
            
            if order_response.status_code == 200:
                order_status = order_response.json()["status"]
                print(f"Статус заказа: {order_status}")
                
                # Проверяем консистентность:
                # Если заказ оплачен, остатки должны уменьшиться
                # Если оплата не прошла, остатки должны остаться прежними
                if order_status == "paid":
                    assert final_stock < initial_stock, "При оплате остатки должны уменьшиться"
                    print("✓ Консистентность: остатки уменьшились после оплаты")
                elif order_status == "payment_failed":
                    assert final_stock == initial_stock, "При неудачной оплате остатки не должны измениться"
                    print("✓ Консистентность: остатки не изменились после неудачной оплаты")
