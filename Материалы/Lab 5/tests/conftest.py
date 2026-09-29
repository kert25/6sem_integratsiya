"""
Фикстуры pytest для UI-тестов
"""
import pytest
import logging
from datetime import datetime
from selenium.webdriver.remote.webdriver import WebDriver
from utils.driver_manager import DriverManager
from utils.logger import setup_logger
from utils.screenshot import ScreenshotManager
from pages.login_page import LoginPage
from pages.tasks_page import TasksPage
from pages.products_page import ProductsPage
from data.test_data import TestData


# Настройка логирования
setup_logger()
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session")
def browser():
    """Фикстура для определения браузера из командной строки"""
    return "chrome"


@pytest.fixture(scope="session")
def headless():
    """Фикстура для определения режима headless"""
    return True


@pytest.fixture(scope="function")
def driver(browser, headless) -> WebDriver:
    """Фикстура для инициализации драйвера"""
    driver_manager = DriverManager(browser=browser, headless=headless)
    driver = driver_manager.create_driver()
    
    yield driver
    
    # Закрытие драйвера после теста
    driver_manager.quit_driver()


@pytest.fixture(scope="function")
def login_page(driver) -> LoginPage:
    """Фикстура для страницы логина"""
    return LoginPage(driver)


@pytest.fixture(scope="function")
def tasks_page(driver) -> TasksPage:
    """Фикстура для страницы задач"""
    return TasksPage(driver)


@pytest.fixture(scope="function")
def products_page(driver) -> ProductsPage:
    """Фикстура для страницы товаров"""
    return ProductsPage(driver)


@pytest.fixture(scope="function")
def logged_in_driver(driver, login_page):
    """Фикстура для драйвера с выполненным входом"""
    login_page.open_login_page()
    login_page.login_with_valid_credentials()
    
    yield driver
    
    # Выход из системы после теста
    try:
        driver.get("http://localhost:8080/logout")
    except Exception:
        pass


@pytest.fixture(scope="function")
def logged_in_tasks_page(logged_in_driver):
    """Фикстура для страницы задач с выполненным входом"""
    tasks_page = TasksPage(logged_in_driver)
    tasks_page.open_tasks_page()
    return tasks_page


@pytest.fixture(scope="function")
def screenshot_on_failure(request, driver):
    """Фикстура для создания скриншотов при падении тестов"""
    screenshot_manager = ScreenshotManager(driver)
    
    yield
    
    # Проверка, упал ли тест
    if request.node.rep_call.failed:
        test_name = request.node.name
        screenshot_manager.take_screenshot(test_name)
        logger.error(f"Тест {test_name} упал. Скриншот сохранен.")


@pytest.fixture(scope="function")
def test_task(logged_in_tasks_page):
    """Фикстура для создания тестовой задачи"""
    task_text = f"Тестовая задача {datetime.now().strftime('%H%M%S')}"
    logged_in_tasks_page.create_task(task_text)
    
    yield task_text
    
    # Очистка: удаление задачи
    try:
        logged_in_tasks_page.delete_task(task_text)
    except Exception:
        pass


@pytest.fixture(scope="function")
def test_product(logged_in_driver):
    """Фикстура для работы с тестовым товаром"""
    products_page = ProductsPage(logged_in_driver)
    products_page.open_products_page()
    
    # Используем первый товар из списка
    product_names = products_page.get_product_names()
    if product_names:
        test_product_name = product_names[0]
        yield products_page, test_product_name
    else:
        yield products_page, ""


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Хук для получения результатов теста"""
    outcome = yield
    rep = outcome.get_result()
    
    # Сохраняем результат в атрибут теста
    setattr(item, "rep_" + rep.when, rep)
