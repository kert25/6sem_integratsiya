# -*- coding: utf-8 -*-
"""Page Object главной страницы the-internet.herokuapp.com."""
from selenium.webdriver.common.by import By
from .base_page import BasePage


class HomePage(BasePage):
    """Главная страница со списком разделов"""

    # Локаторы
    HEADING = (By.CSS_SELECTOR, "h1.heading")
    INPUTS_LINK = (By.LINK_TEXT, "Inputs")
    NOTIFICATION_MESSAGES_LINK = (By.LINK_TEXT, "Notification Messages")
    GEOLOCATION_LINK = (By.LINK_TEXT, "Geolocation")

    def open_home_page(self):
        """Открытие главной страницы"""
        self.open("")

    def get_heading_text(self) -> str:
        """Текст заголовка главной страницы"""
        return self.get_text(self.HEADING)

    def open_inputs(self) -> "HomePage":
        """Переход в раздел Inputs по ссылке"""
        self.click(self.INPUTS_LINK)
        return self

    def open_notification_messages(self) -> "HomePage":
        """Переход в раздел Notification Messages по ссылке"""
        self.click(self.NOTIFICATION_MESSAGES_LINK)
        return self

    def open_geolocation(self) -> "HomePage":
        """Переход в раздел Geolocation по ссылке"""
        self.click(self.GEOLOCATION_LINK)
        return self
