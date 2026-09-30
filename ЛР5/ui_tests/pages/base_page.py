# -*- coding: utf-8 -*-
"""
Базовый класс для всех страниц (the-internet.herokuapp.com).
Поиск элементов, клики, ввод текста, явные ожидания, логирование.
"""
import logging
import os
from datetime import datetime
from typing import Tuple, List, Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException,
    StaleElementReferenceException, ElementNotInteractableException,
    ElementClickInterceptedException
)
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


class BasePage:
    """Базовый класс для всех страниц веб-приложения"""

    DEFAULT_BASE_URL = "https://the-internet.herokuapp.com"

    def __init__(self, driver: WebDriver, base_url: Optional[str] = None):
        self.driver = driver
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self.wait = WebDriverWait(driver, 10)
        self.actions = ActionChains(driver)
        self.logger = logging.getLogger(self.__class__.__name__)

    def open(self, url: str = ""):
        """Открытие страницы по относительному URL"""
        full_url = f"{self.base_url}/{url.lstrip('/')}"
        self.logger.info(f"Открытие страницы: {full_url}")
        self.driver.get(full_url)

    def find_element(self, locator: Tuple[By, str], timeout: int = 10) -> WebElement:
        """Поиск элемента с ожиданием"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located(locator))
            self.logger.debug(f"Элемент найден: {locator}")
            return element
        except TimeoutException:
            self.logger.error(f"Элемент не найден: {locator}")
            raise

    def find_elements(self, locator: Tuple[By, str], timeout: int = 10) -> List[WebElement]:
        """Поиск нескольких элементов"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            elements = wait.until(EC.presence_of_all_elements_located(locator))
            self.logger.debug(f"Найдено элементов: {len(elements)}")
            return elements
        except TimeoutException:
            self.logger.warning(f"Элементы не найдены: {locator}")
            return []

    def wait_for_element_visible(self, locator: Tuple[By, str], timeout: int = 10) -> WebElement:
        """Ожидание видимости элемента"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            self.logger.debug(f"Элемент видим: {locator}")
            return element
        except TimeoutException:
            self.logger.error(f"Элемент не стал видимым: {locator}")
            raise

    def wait_for_element_clickable(self, locator: Tuple[By, str], timeout: int = 10) -> WebElement:
        """Ожидание кликабельности элемента"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.element_to_be_clickable(locator)
            )
            self.logger.debug(f"Элемент кликабелен: {locator}")
            return element
        except TimeoutException:
            self.logger.error(f"Элемент не стал кликабельным: {locator}")
            raise

    def click(self, locator: Tuple[By, str], timeout: int = 10):
        """Клик по элементу"""
        try:
            element = self.wait_for_element_clickable(locator, timeout)
            element.click()
            self.logger.info(f"Клик по элементу: {locator}")
        except (ElementNotInteractableException, ElementClickInterceptedException,
                StaleElementReferenceException) as e:
            self.logger.error(f"Ошибка при клике: {e}")
            # Попытка клика через JavaScript
            element = self.find_element(locator, timeout)
            self.driver.execute_script("arguments[0].click();", element)

    def input_text(self, locator: Tuple[By, str], text: str, timeout: int = 10):
        """Ввод текста в поле"""
        element = self.wait_for_element_visible(locator, timeout)
        element.clear()
        element.send_keys(text)
        self.logger.info(f"Ввод текста '{text}' в элемент: {locator}")

    def get_text(self, locator: Tuple[By, str], timeout: int = 10) -> str:
        """Получение текста элемента"""
        element = self.wait_for_element_visible(locator, timeout)
        text = element.text
        self.logger.debug(f"Текст элемента {locator}: {text}")
        return text

    def get_attribute(self, locator: Tuple[By, str], attribute: str, timeout: int = 10) -> str:
        """Получение атрибута элемента"""
        element = self.find_element(locator, timeout)
        value = element.get_attribute(attribute)
        self.logger.debug(f"Атрибут {attribute} элемента {locator}: {value}")
        return value

    def is_element_present(self, locator: Tuple[By, str], timeout: int = 5) -> bool:
        """Проверка наличия элемента"""
        try:
            self.find_element(locator, timeout)
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    def is_element_visible(self, locator: Tuple[By, str], timeout: int = 5) -> bool:
        """Проверка видимости элемента"""
        try:
            self.wait_for_element_visible(locator, timeout)
            return True
        except TimeoutException:
            return False

    def scroll_to_element(self, locator: Tuple[By, str], timeout: int = 10):
        """Прокрутка к элементу"""
        element = self.find_element(locator, timeout)
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        self.logger.debug(f"Прокрутка к элементу: {locator}")

    def accept_alert(self):
        """Принятие алерта"""
        alert = self.driver.switch_to.alert
        alert.accept()
        self.logger.debug("Алерт принят")

    def dismiss_alert(self):
        """Отклонение алерта"""
        alert = self.driver.switch_to.alert
        alert.dismiss()
        self.logger.debug("Алерт отклонен")

    def take_screenshot(self, name: str = "screenshot"):
        """Создание скриншота страницы"""
        os.makedirs("screenshots", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join("screenshots", f"{name}_{timestamp}.png")
        self.driver.save_screenshot(filename)
        self.logger.info(f"Скриншот сохранен: {filename}")
        return filename
