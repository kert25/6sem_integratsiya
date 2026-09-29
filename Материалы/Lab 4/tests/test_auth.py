"""
Автоматизированные тесты для API аутентификации
"""
import pytest
from api.schemas import AuthResponse, User, ErrorResponse


class TestAuthAPI:
    """Тесты для эндпоинтов аутентификации"""
    
    def test_login_success(self, auth_api):
        """Тест успешной аутентификации"""
        response = auth_api.login("student@university.ru", "password123")
        assert response.status_code == 200
        
        auth_data = AuthResponse.parse_obj(response.json())
        assert len(auth_data.token) > 0
        assert auth_data.user.email == "student@university.ru"
    
    @pytest.mark.parametrize("email, password, expected_error", [
        ("wrong@email.com", "password123", "Неверный email или пароль"),
        ("student@university.ru", "wrongpass", "Неверный email или пароль"),
        ("", "password123", "Требуются email и password"),
        ("student@university.ru", "", "Требуются email и password"),
    ])
    def test_login_failure(self, auth_api, email, password, expected_error):
        """Тест неуспешной аутентификации"""
        response = auth_api.login(email, password)
        assert response.status_code in [400, 401]
        
        error = ErrorResponse.parse_obj(response.json())
        assert expected_error in error.error
    
    def test_register_new_user(self, auth_api, faker):
        """Тест регистрации нового пользователя"""
        email = faker.email()
        password = faker.password()
        name = faker.name()
        
        response = auth_api.register(email, password, name)
        assert response.status_code == 201
        
        user_id = response.json()['userId']
        assert user_id > 0
    
    def test_register_duplicate_email(self, auth_api):
        """Тест регистрации с существующим email"""
        response = auth_api.register(
            "student@university.ru",
            "newpassword",
            "Новый пользователь"
        )
        assert response.status_code == 409
        
        error = ErrorResponse.parse_obj(response.json())
        assert "уже существует" in error.error
    
    def test_get_current_user_authenticated(self, auth_api, authenticated_client):
        """Тест получения данных текущего пользователя (с аутентификацией)"""
        # Используем auth_api с тем же клиентом
        from api.client import AuthAPI
        auth_api_with_token = AuthAPI(authenticated_client)
        
        response = auth_api_with_token.get_current_user()
        assert response.status_code == 200
        
        user = User.parse_obj(response.json())
        assert user.email == "student@university.ru"
    
    def test_get_current_user_unauthenticated(self, auth_api):
        """Тест получения данных пользователя без аутентификации"""
        response = auth_api.get_current_user()
        assert response.status_code == 401
        
        error = ErrorResponse.parse_obj(response.json())
        assert "аутентификации" in error.error.lower()
    
    def test_full_auth_flow(self, auth_api, faker):
        """Полный цикл аутентификации: регистрация -> вход -> получение данных"""
        # 1. Регистрация
        email = faker.email()
        password = faker.password()
        name = faker.name()
        
        response = auth_api.register(email, password, name)
        assert response.status_code == 201
        
        # 2. Вход
        response = auth_api.login(email, password)
        assert response.status_code == 200
        
        auth_data = AuthResponse.parse_obj(response.json())
        token = auth_data.token
        
        # 3. Получение данных (с токеном)
        from api.client import APIClient, AuthAPI
        client = APIClient(base_url="http://localhost:5000")
        client.set_auth_token(token)
        
        auth_api_with_token = AuthAPI(client)
        response = auth_api_with_token.get_current_user()
        assert response.status_code == 200
        
        user = User.parse_obj(response.json())
        assert user.email == email
        assert user.name == name