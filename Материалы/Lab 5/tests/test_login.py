"""
Тесты для страницы авторизации
"""
import pytest
import time
from pages.login_page import LoginPage
from data.test_data import TestData


class TestLogin:
    """Тесты авторизации"""
    
    def test_successful_login(self, login_page):
        """Тест успешного входа"""
        # Открываем страницу логина
        login_page.open_login_page()
        
        # Выполняем вход с валидными данными
        login_page.login_with_valid_credentials()
        
        # Проверяем успешный вход
        assert login_page.is_login_successful(), "Вход не выполнен"
        
        # Проверяем изменение URL
        assert "/tasks" in login_page.driver.current_url or "/dashboard" in login_page.driver.current_url
    
    @pytest.mark.parametrize("username, password", [
        (TestData.INVALID_USERNAME, TestData.INVALID_PASSWORD),
        ("", TestData.VALID_PASSWORD),
        (TestData.VALID_USERNAME, ""),
        ("", ""),
        ("not_existing_user", "wrong_password"),
    ])
    def test_login_with_invalid_credentials(self, login_page, username, password):
        """Тест входа с невалидными данными"""
        login_page.open_login_page()
        login_page.login(username, password)
        
        # Проверяем сообщение об ошибке
        error_message = login_page.get_error_message()
        assert error_message, "Сообщение об ошибке не отображается"
        assert "неверный" in error_message.lower() or "обязательно" in error_message.lower()
    
    def test_login_with_remember_me(self, login_page):
        """Тест входа с флажком 'Запомнить меня'"""
        login_page.open_login_page()
        login_page.login(TestData.VALID_USERNAME, TestData.VALID_PASSWORD, remember_me=True)
        
        assert login_page.is_login_successful(), "Вход не выполнен"
        
        # Проверяем, что куки сохранены
        cookies = login_page.driver.get_cookies()
        remember_cookie = any(cookie['name'] == 'remember_me' for cookie in cookies)
        assert remember_cookie, "Куки 'remember_me' не установлены"
    
    def test_login_form_validation(self, login_page):
        """Тест валидации формы"""
        login_page.open_login_page()
        
        # Проверяем, что поля обязательны
        login_page.clear_login_form()
        
        # Пытаемся войти без данных
        login_button_enabled = login_page.is_login_button_enabled()
        
        # В зависимости от реализации, кнопка может быть disabled
        # или показываться сообщение об ошибке при клике
        if login_button_enabled:
            login_page.click(login_page.LOGIN_BUTTON)
            error_message = login_page.get_error_message()
            assert error_message, "Сообщение об ошибке не отображается"
    
    def test_forgot_password_link(self, login_page):
        """Тест ссылки 'Забыли пароль?'"""
        login_page.open_login_page()
        login_page.click_forgot_password()
        
        # Проверяем переход на страницу восстановления пароля
        assert "forgot-password" in login_page.driver.current_url.lower() or \
               "reset" in login_page.driver.current_url.lower()
    
    def test_register_link(self, login_page):
        """Тест ссылки 'Регистрация'"""
        login_page.open_login_page()
        login_page.click_register()
        
        # Проверяем переход на страницу регистрации
        assert "register" in login_page.driver.current_url.lower() or \
               "signup" in login_page.driver.current_url.lower()
    
    def test_password_masking(self, login_page):
        """Тест маскировки пароля"""
        login_page.open_login_page()
        
        # Вводим пароль
        login_page.input_text(login_page.PASSWORD_INPUT, "secret_password")
        
        # Проверяем, что пароль скрыт
        password_field = login_page.find_element(login_page.PASSWORD_INPUT)
        input_type = password_field.get_attribute("type")
        
        assert input_type == "password", f"Пароль не маскируется, type={input_type}"
    
    @pytest.mark.slow
    def test_login_after_multiple_failed_attempts(self, login_page):
        """Тест блокировки после нескольких неудачных попыток"""
        login_page.open_login_page()
        
        # Несколько неудачных попыток входа
        for i in range(5):
            login_page.login(f"wrong_user_{i}", "wrong_password")
            time.sleep(0.5)
        
        # Последняя попытка с правильными данными
        login_page.login_with_valid_credentials()
        
        # Проверяем, возможно ли войти или аккаунт заблокирован
        error_message = login_page.get_error_message()
        
        # В зависимости от реализации системы
        # Может быть сообщение о блокировке или успешный вход
        if error_message:
            assert "блокиров" in error_message.lower() or \
                   "попыток" in error_message.lower()
