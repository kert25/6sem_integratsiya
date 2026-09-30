# -*- coding: utf-8 -*-
"""Фикстуры pytest для UI-тестов the-internet.herokuapp.com."""
import logging
import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from utils.driver_manager import DriverManager
from utils.logger import setup_logger
from utils.screenshot import ScreenshotManager
from pages.home_page import HomePage
from pages.inputs_page import InputsPage
from pages.notification_messages_page import NotificationMessagesPage
from pages.geolocation_page import GeolocationPage


# Настройка логирования
setup_logger()
logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    """Параметры командной строки: браузер и режим headless"""
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        choices=["chrome", "firefox", "edge"],
        help="Браузер: chrome, firefox или edge",
    )
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Запуск браузера в headless-режиме",
    )


@pytest.fixture(scope="session")
def browser(request):
    """Браузер из командной строки (--browser)"""
    return request.config.getoption("--browser")


@pytest.fixture(scope="session")
def headless(request):
    """Режим headless из командной строки (--headless)"""
    return request.config.getoption("--headless")


@pytest.fixture(scope="function")
def driver(browser, headless) -> WebDriver:
    """Фикстура для инициализации драйвера"""
    driver_manager = DriverManager(browser=browser, headless=headless)
    driver = driver_manager.create_driver()

    yield driver

    # Закрытие драйвера после теста
    driver_manager.quit_driver()


@pytest.fixture(scope="function")
def home_page(driver) -> HomePage:
    """Фикстура главной страницы"""
    return HomePage(driver)


@pytest.fixture(scope="function")
def inputs_page(driver) -> InputsPage:
    """Фикстура страницы Inputs"""
    return InputsPage(driver)


@pytest.fixture(scope="function")
def notification_messages_page(driver) -> NotificationMessagesPage:
    """Фикстура страницы Notification Messages"""
    return NotificationMessagesPage(driver)


@pytest.fixture(scope="function")
def geolocation_page(driver) -> GeolocationPage:
    """Фикстура страницы Geolocation"""
    return GeolocationPage(driver)


@pytest.fixture(scope="function", autouse=True)
def screenshot_on_failure(request, driver):
    """Фикстура для создания скриншотов при падении тестов"""
    screenshot_manager = ScreenshotManager(driver)

    yield

    # Проверка, упал ли тест
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        test_name = request.node.name
        screenshot_manager.take_screenshot(f"FAIL_{test_name}")
        logger.error(f"Тест {test_name} упал. Скриншот сохранен.")


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Хук для получения результатов теста"""
    outcome = yield
    rep = outcome.get_result()

    # Сохраняем результат в атрибут теста
    setattr(item, "rep_" + rep.when, rep)
