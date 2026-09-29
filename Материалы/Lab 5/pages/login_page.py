"""
Page Object для страницы авторизации
"""
from selenium.webdriver.common.by import By
from .base_page import BasePage
from ..data.test_data import TestData


class LoginPage(BasePage):
    """Страница авторизации"""
    
    # Локаторы
    USERNAME_INPUT = (By.ID, "username")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-btn")
    ERROR_MESSAGE = (By.CLASS_NAME, "error-message")
    REMEMBER_ME_CHECKBOX = (By.ID, "remember-me")
    FORGOT_PASSWORD_LINK = (By.LINK_TEXT, "Забыли пароль?")
    REGISTER_LINK = (By.LINK_TEXT, "Регистрация")
    
    def __init__(self, driver):
        super().__init__(driver)
        self.base_url = "http://localhost:8080/login"
    
    def open_login_page(self):
        """Открытие страницы логина"""
        self.open("/login")
    
    def login(self, username: str, password: str, remember_me: bool = False):
        """Выполнение входа в систему"""
        self.logger.info(f"Вход пользователя: {username}")
        
        self.input_text(self.USERNAME_INPUT, username)
        self.input_text(self.PASSWORD_INPUT, password)
        
        if remember_me:
            if not self.is_checkbox_checked(self.REMEMBER_ME_CHECKBOX):
                self.click(self.REMEMBER_ME_CHECKBOX)
        
        self.click(self.LOGIN_BUTTON)
    
    def login_with_valid_credentials(self):
        """Вход с валидными учетными данными"""
        self.login(TestData.VALID_USERNAME, TestData.VALID_PASSWORD)
    
    def login_with_invalid_credentials(self):
        """Вход с невалидными учетными данными"""
        self.login(TestData.INVALID_USERNAME, TestData.INVALID_PASSWORD)
    
    def get_error_message(self) -> str:
        """Получение сообщения об ошибке"""
        if self.is_element_visible(self.ERROR_MESSAGE):
            return self.get_text(self.ERROR_MESSAGE)
        return ""
    
    def is_login_successful(self) -> bool:
        """Проверка успешного входа"""
        # Проверяем, что URL изменился (например, на /dashboard)
        return "/dashboard" in self.driver.current_url or "/tasks" in self.driver.current_url
    
    def click_forgot_password(self):
        """Клик по ссылке 'Забыли пароль?'"""
        self.click(self.FORGOT_PASSWORD_LINK)
    
    def click_register(self):
        """Клик по ссылке 'Регистрация'"""
        self.click(self.REGISTER_LINK)
    
    def clear_login_form(self):
        """Очистка формы логина"""
        self.find_element(self.USERNAME_INPUT).clear()
        self.find_element(self.PASSWORD_INPUT).clear()
    
    def is_login_button_enabled(self) -> bool:
        """Проверка доступности кнопки входа"""
        return self.find_element(self.LOGIN_BUTTON).is_enabled()
