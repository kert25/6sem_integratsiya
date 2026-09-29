"""
Автоматизированные тесты для API товаров
"""
import pytest
from api.schemas import ProductList, Product


class TestProductsAPI:
    """Тесты для эндпоинтов товаров"""
    
    def test_get_all_products(self, api_client):
        """Тест получения списка товаров"""
        response = api_client.get('/api/v1/products')
        assert response.status_code == 200
        
        product_list = ProductList.parse_obj(response.json())
        assert product_list.count > 0
        assert len(product_list.products) == product_list.count
    
    @pytest.mark.parametrize("category,expected_count", [
        ("Электроника", 1),
        ("Книги", 1),
        ("Продукты", 1),
        ("Одежда", 1),
        ("Несуществующая", 0),
    ])
    def test_filter_products_by_category(self, api_client, category, expected_count):
        """Тест фильтрации товаров по категории"""
        response = api_client.get('/api/v1/products', params={'category': category})
        assert response.status_code == 200
        
        product_list = ProductList.parse_obj(response.json())
        
        if expected_count > 0:
            assert product_list.count == expected_count
            for product in product_list.products:
                assert product.category == category
        else:
            assert product_list.count == 0
    
    def test_filter_products_in_stock(self, api_client):
        """Тест фильтрации товаров в наличии"""
        response = api_client.get('/api/v1/products', params={'inStock': 'true'})
        assert response.status_code == 200
        
        product_list = ProductList.parse_obj(response.json())
        
        for product in product_list.products:
            assert product.stock > 0
    
    @pytest.mark.parametrize("min_price,max_price", [
        (0, 1000),
        (1000, 5000),
        (50000, 100000),
    ])
    def test_filter_products_by_price(self, api_client, min_price, max_price):
        """Тест фильтрации товаров по цене"""
        params = {
            'minPrice': min_price,
            'maxPrice': max_price
        }
        
        response = api_client.get('/api/v1/products', params=params)
        assert response.status_code == 200
        
        product_list = ProductList.parse_obj(response.json())
        
        for product in product_list.products:
            assert min_price <= product.price <= max_price
    
    def test_get_product_by_id(self, api_client):
        """Тест получения товара по ID"""
        # Сначала получаем список товаров
        response = api_client.get('/api/v1/products')
        product_id = response.json()['products'][0]['id']
        
        # Получаем товар по ID
        response = api_client.get(f'/api/v1/products/{product_id}')
        assert response.status_code == 200
        
        product = Product.parse_obj(response.json())
        assert product.id == product_id
    
    def test_get_nonexistent_product(self, api_client):
        """Тест получения несуществующего товара"""
        response = api_client.get('/api/v1/products/99999')
        assert response.status_code == 404
