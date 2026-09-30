# -*- coding: utf-8 -*-
"""Page Object страницы Notification Messages (flash-уведомления)."""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from .base_page import BasePage
from data.test_data import TestData


class NotificationMessagesPage(BasePage):
    """Страница раздела Notification Messages"""

    # Локаторы
    HEADING = (By.CSS_SELECTOR, "div.example h3")
    CLICK_HERE_LINK = (By.LINK_TEXT, "Click here")
    FLASH = (By.ID, "flash")
    FLASH_CLOSE = (By.CSS_SELECTOR, "#flash a.close")

    def open_notification_page(self):
        """Открытие страницы Notification Messages напрямую"""
        self.open("notification_message")

    def get_heading_text(self) -> str:
        """Текст заголовка страницы"""
        return self.get_text(self.HEADING)

    def click_here(self):
        """Клик по ссылке 'Click here' — загружает новое сообщение"""
        self.click(self.CLICK_HERE_LINK)
        self.logger.info("Выполнен клик 'Click here'")

    def wait_flash_visible(self, timeout: int = 10):
        """Ожидание появления flash-уведомления"""
        WebDriverWait(self.driver, timeout).until(
            EC.visibility_of_element_located(self.FLASH)
        )
        self.logger.info("Flash-уведомление отображается")

    def get_flash_text(self) -> str:
        """Текст flash-уведомления (нормализованный)"""
        text = self.get_text(self.FLASH)
        return " ".join(text.split())

    def flash_text_is_known(self) -> bool:
        """Проверка, что текст уведомления — один из ожидаемых вариантов"""
        text = self.get_flash_text()
        return any(text.startswith(expected) for expected in TestData.NOTIFICATION_TEXTS)

    def close_flash(self):
        """Закрытие уведомления крестиком"""
        self.click(self.FLASH_CLOSE)
        self.logger.info("Flash-уведомление закрыто")

    def is_flash_visible(self) -> bool:
        """Видимость flash-уведомления"""
        return self.is_element_visible(self.FLASH)
