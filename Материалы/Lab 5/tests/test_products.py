"""
Тесты для страницы товаров
"""
import pytest
from pages.products_page import ProductsPage
from data.test_data import TestData


class TestProducts:
    """Тесты каталога товаров"""
    
    def test_products_page_loads(self, logged_in_driver):
        """Тест загрузки страницы товаров"""
        products_page = ProductsPage(logged_in_driver)
        products_page.open_products_page()
        
        # Проверяем основные элементы
        assert products_page.is_element_present(products_page.PRODUCT_LIST), "Список товаров не отображается"
        assert products_page.is_element_present(products_page.SEARCH_INPUT), "Поле поиска не отображается"
    
    def test_search_product(self, logged_in_driver):
        """Тест поиска товара"""
        products_page = ProductsPage(logged_in_driver)
        products_page.open_products_page()
        
        # Получаем список всех товаров
        all_products = products_page.get_product_names()
        
        if all_products:
            # Ищем первый товар
            search_term = all_products[0].split()[0]  # Первое слово названия
            products_page.search_product(search_term)
            
            # Проверяем результаты поиска
            search_results = products_page.get_product_names()
            
            for product in search_results:
                assert search_term.lower() in product.lower(), \
                    f"Товар '{product}' не содержит '{search_term}'"
    
    def test_filter_by_category(self, logged_in_driver):
        """Тест фильтрации по категории"""
        products_page = ProductsPage(logged_in_driver)
        products_page.open_products_page()
        
        # Если есть фильтр по категориям
        if products_page.is_element_present(products_page.CATEGORY_FILTER):
            # Фильтруем по первой доступной категории
            products_page.filter_by_category("Электроника")
            
            # Даем время на применение фильтра
            products_page.wait_for_element_visible(products_page.PRODUCT_LIST)
            
            # Проверяем, что товары отфильтрованы
            # (конкретная проверка зависит от реализации)
    
    def test_sort_products(self, logged_in_driver):
        """Тест сортировки товаров"""
        products_page = ProductsPage(logged_in_driver)
        products_page.open_products_page()
        
        # Если есть сортировка
        if products_page.is_element_present(products_page.SORT_SELECT):
            # Сортируем по цене (по возрастанию)
            products_page.sort_products("Цена: по возрастанию")
            
            # Получаем цены после сортировки
            prices = products_page.get_product_prices()
            
            # Проверяем, что цены отсортированы по возрастанию
            assert prices == sorted(prices), "Цены не отсортированы по возрастанию"
            
            # Сортируем по цене (по убыванию)
            products_page.sort_products("Цена: по убыванию")
            
            # Получаем цены после сортировки
            prices_desc = products_page.get_product_prices()
            
            # Проверяем, что цены отсортированы по убыванию
            assert prices_desc == sorted(prices_desc, reverse=True), \
                "Цены не отсортированы по убыванию"
    
    def test_add_to_cart(self, test_product):
        """Тест добавления товара в корзину"""
        products_page, product_name = test_product
        
        if not product_name:
            pytest.skip("Нет товаров для тестирования")
        
        # Получаем начальное количество товаров в корзине
        initial_cart_count = products_page.get_cart_count()
        
        # Добавляем товар в корзину
        products_page.add_product_to_cart(product_name)
        
        # Проверяем увеличение счетчика корзины
        new_cart_count = products_page.get_cart_count()
        assert new_cart_count == initial_cart_count + 1, \
            f"Счетчик корзины не увеличился: {initial_cart_count} -> {new_cart_count}"
    
    def test_cart_navigation(self, logged_in_driver):
        """Тест перехода в корзину"""
        products_page = ProductsPage(logged_in_driver)
        products_page.open_products_page()
        
        # Переходим в корзину
        products_page.go_to_cart()
        
        # Проверяем, что перешли на страницу корзины
        assert "cart" in products_page.driver.current_url.lower(), \
            f"Не перешли в корзину, URL: {products_page.driver.current_url}"
    
    def test_pagination(self, logged_in_driver):
        """Тест пагинации"""
        products_page = ProductsPage(logged_in_driver)
        products_page.open_products_page()
        
        # Если есть пагинация
        if products_page.is_element_present(products_page.PAGINATION_NEXT):
            # Переходим на следующую страницу
            products_page.go_to_next_page()
            
            # Проверяем, что URL изменился (добавился параметр страницы)
            assert "page=2" in products_page.driver.current_url or \
                   "p=2" in products_page.driver.current_url, \
                   "Не перешли на следующую страницу"
            
            # Возвращаемся на предыдущую страницу
            if products_page.is_element_present(products_page.PAGINATION_PREV):
                products_page.go_to_prev_page()
                
                # Проверяем возврат на первую страницу
                assert "page=1" in products_page.driver.current_url or \
                       not any(param in products_page.driver.current_url 
                               for param in ["page=", "p="]), \
                       "Не вернулись на первую страницу"
    
    def test_product_details_display(self, logged_in_driver):
        """Тест отображения деталей товара"""
        products_page = ProductsPage(logged_in_driver)
        products_page.open_products_page()
        
        # Получаем информацию о товарах
        product_names = products_page.get_product_names()
        product_prices = products_page.get_product_prices()
        
        # Проверяем, что у всех товаров есть названия и цены
        assert len(product_names) == len(product_prices), \
            f"Количество названий ({len(product_names)}) не совпадает с количеством цен ({len(product_prices)})"
        
        if product_names:
            # Проверяем, что названия не пустые
            for name in product_names:
                assert name.strip(), "Найдено пустое название товара"
            
            # Проверяем, что цены положительные
            for price in product_prices:
                assert price > 0, f"Найдена неположительная цена: {price}"
    
    @pytest.mark.integration
    def test_search_and_add_to_cart_flow(self, logged_in_driver):
        """Интеграционный тест: поиск и добавление в корзину"""
        products_page = ProductsPage(logged_in_driver)
        products_page.open_products_page()
        
        # Получаем все товары
        all_products = products_page.get_product_names()
        
        if len(all_products) >= 2:
            # Ищем товар
            search_term = all_products[0].split()[0]
            products_page.search_product(search_term)
            
            # Добавляем найденный товар в корзину
            products_page.add_product_to_cart(all_products[0])
            
            # Проверяем счетчик корзины
            cart_count = products_page.get_cart_count()
            assert cart_count > 0, "Товар не добавлен в корзину"
            
            # Переходим в корзину
            products_page.go_to_cart()
            
            # Проверяем, что в корзине есть товары
            assert "cart" in products_page.driver.current_url.lower()
