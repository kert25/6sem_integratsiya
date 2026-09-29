"""
Page Object для страницы товаров
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from .base_page import BasePage


class ProductsPage(BasePage):
    """Страница каталога товаров"""
    
    # Локаторы
    SEARCH_INPUT = (By.ID, "search-input")
    SEARCH_BUTTON = (By.ID, "search-btn")
    PRODUCT_LIST = (By.CLASS_NAME, "product-list")
    PRODUCT_ITEMS = (By.CLASS_NAME, "product-item")
    PRODUCT_NAME = (By.CLASS_NAME, "product-name")
    PRODUCT_PRICE = (By.CLASS_NAME, "product-price")
    ADD_TO_CART_BUTTON = (By.CLASS_NAME, "add-to-cart")
    CATEGORY_FILTER = (By.ID, "category-filter")
    SORT_SELECT = (By.ID, "sort-select")
    CART_ICON = (By.ID, "cart-icon")
    CART_COUNT = (By.ID, "cart-count")
    PAGINATION_NEXT = (By.CLASS_NAME, "next-page")
    PAGINATION_PREV = (By.CLASS_NAME, "prev-page")
    
    def __init__(self, driver):
        super().__init__(driver)
        self.base_url = "http://localhost:8080/products"
    
    def open_products_page(self):
        """Открытие страницы товаров"""
        self.open("/products")
    
    def search_product(self, search_term: str):
        """Поиск товара"""
        self.logger.info(f"Поиск товара: {search_term}")
        
        self.input_text(self.SEARCH_INPUT, search_term)
        self.click(self.SEARCH_BUTTON)
    
    def get_product_names(self) -> list:
        """Получение названий всех товаров"""
        products = []
        if self.is_element_present(self.PRODUCT_ITEMS):
            name_elements = self.find_elements(self.PRODUCT_NAME)
            products = [name.text for name in name_elements]
        return products
    
    def get_product_prices(self) -> list:
        """Получение цен всех товаров"""
        prices = []
        if self.is_element_present(self.PRODUCT_ITEMS):
            price_elements = self.find_elements(self.PRODUCT_PRICE)
            prices = [float(price.text.replace("$", "").replace("€", "").strip()) 
                     for price in price_elements]
        return prices
    
    def add_product_to_cart(self, product_name: str):
        """Добавление товара в корзину"""
        self.logger.info(f"Добавление товара в корзину: {product_name}")
        
        product_items = self.find_elements(self.PRODUCT_ITEMS)
        for item in product_items:
            name_element = item.find_element(*self.PRODUCT_NAME)
            if name_element.text == product_name:
                add_button = item.find_element(*self.ADD_TO_CART_BUTTON)
                add_button.click()
                break
    
    def filter_by_category(self, category: str):
        """Фильтрация товаров по категории"""
        self.logger.info(f"Фильтрация по категории: {category}")
        
        filter_select = Select(self.find_element(self.CATEGORY_FILTER))
        filter_select.select_by_visible_text(category)
    
    def sort_products(self, sort_option: str):
        """Сортировка товаров"""
        self.logger.info(f"Сортировка товаров: {sort_option}")
        
        sort_select = Select(self.find_element(self.SORT_SELECT))
        sort_select.select_by_visible_text(sort_option)
    
    def get_cart_count(self) -> int:
        """Получение количества товаров в корзине"""
        if self.is_element_present(self.CART_COUNT):
            count_text = self.get_text(self.CART_COUNT)
            return int(count_text) if count_text.isdigit() else 0
        return 0
    
    def go_to_cart(self):
        """Переход в корзину"""
        self.click(self.CART_ICON)
    
    def go_to_next_page(self):
        """Переход на следующую страницу"""
        if self.is_element_present(self.PAGINATION_NEXT):
            self.click(self.PAGINATION_NEXT)
    
    def go_to_prev_page(self):
        """Переход на предыдущую страницу"""
        if self.is_element_present(self.PAGINATION_PREV):
            self.click(self.PAGINATION_PREV)
