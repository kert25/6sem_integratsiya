# -*- coding: utf-8 -*-
"""
Автоматизированные тесты для API товаров
"""
import pytest
from api.schemas import ProductList, Product, ErrorResponse


class TestProductsAPI:
    """Тесты для эндпоинтов товаров"""

    @pytest.mark.smoke
    def test_get_all_products(self, products_api):
        """Тест получения списка товаров"""
        response = products_api.get_products()
        assert response.status_code == 200

        product_list = ProductList.model_validate(response.json())
        assert product_list.count > 0
        assert len(product_list.products) == product_list.count

    @pytest.mark.parametrize("category, expected_count", [
        ("Электроника", 1),
        ("Книги", 1),
        ("Продукты", 1),
        ("Одежда", 1),
        ("Несуществующая", 0),
    ])
    def test_filter_products_by_category(self, products_api, category, expected_count):
        """Тест фильтрации товаров по категории (параметризованный)"""
        response = products_api.get_products(category=category)
        assert response.status_code == 200

        product_list = ProductList.model_validate(response.json())

        if expected_count > 0:
            assert product_list.count == expected_count
            for product in product_list.products:
                assert product.category == category
        else:
            assert product_list.count == 0

    def test_filter_products_in_stock(self, products_api):
        """Тест фильтрации товаров в наличии (граничный: товар со stock=0)"""
        response = products_api.get_products(in_stock=True)
        assert response.status_code == 200

        product_list = ProductList.model_validate(response.json())

        # Товар "Футболка" (stock=0) должен быть исключен
        for product in product_list.products:
            assert product.stock > 0
        assert product_list.count == 3

    @pytest.mark.parametrize("min_price, max_price", [
        (0, 1000),
        (1000, 5000),
        (50000, 100000),
    ])
    def test_filter_products_by_price(self, products_api, min_price, max_price):
        """Тест фильтрации товаров по цене (граничные диапазоны, параметризованный)"""
        response = products_api.get_products(min_price=min_price, max_price=max_price)
        assert response.status_code == 200

        product_list = ProductList.model_validate(response.json())

        for product in product_list.products:
            assert min_price <= product.price <= max_price

    def test_get_product_by_id(self, products_api):
        """Тест получения товара по ID"""
        # Сначала получаем список товаров
        response = products_api.get_products()
        product_id = response.json()['products'][0]['id']

        # Получаем товар по ID
        response = products_api.get_product(product_id)
        assert response.status_code == 200

        product = Product.model_validate(response.json())
        assert product.id == product_id

    @pytest.mark.negative
    def test_get_nonexistent_product(self, products_api):
        """Тест получения несуществующего товара"""
        response = products_api.get_product(99999)
        assert response.status_code == 404

        error = ErrorResponse.model_validate(response.json())
        assert "не найден" in error.error.lower()
