# -*- coding: utf-8 -*-
"""Page Object страницы Geolocation (определение координат)."""
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from .base_page import BasePage
from data.test_data import TestData


class GeolocationPage(BasePage):
    """Страница раздела Geolocation"""

    # Локаторы
    HEADING = (By.CSS_SELECTOR, "div.example h3")
    DEMO_TEXT = (By.ID, "demo")
    WHERE_AM_I_BUTTON = (By.XPATH, "//button[contains(., 'Where am I')]")
    LAT_VALUE = (By.ID, "lat-value")
    LONG_VALUE = (By.ID, "long-value")
    MAPS_LINK = (By.PARTIAL_LINK_TEXT, "See it on Google")

    def open_geolocation_page(self):
        """Открытие страницы Geolocation напрямую"""
        self.open("geolocation")

    def get_heading_text(self) -> str:
        """Текст заголовка страницы"""
        return self.get_text(self.HEADING)

    def get_demo_text(self) -> str:
        """Текст абзаца #demo (приглашение либо координаты)"""
        return " ".join(self.get_text(self.DEMO_TEXT).split())

    def mock_geolocation(self, latitude: float = None, longitude: float = None):
        """Подмена navigator.geolocation.getCurrentPosition стаб-координатами.

        В headless-браузерах реальное определение местоположения недоступно,
        поэтому перед кликом подменяется браузерный API Geolocation:
        любой запрос позиции мгновенно возвращает заданные координаты
        (детерминированно в Chrome и Firefox, без системных разрешений).
        """
        latitude = TestData.MOCK_LATITUDE if latitude is None else latitude
        longitude = TestData.MOCK_LONGITUDE if longitude is None else longitude
        payload = json.dumps({"coords": {"latitude": latitude, "longitude": longitude}})
        self.driver.execute_script(
            "navigator.geolocation.getCurrentPosition = "
            "function(success){ success(" + payload + "); };"
        )
        self.logger.info(f"Geolocation подменен: lat={latitude}, long={longitude}")

    def click_where_am_i(self):
        """Клик по кнопке 'Where am I?'"""
        self.click(self.WHERE_AM_I_BUTTON)
        self.logger.info("Выполнен клик 'Where am I?'")

    def wait_coordinates_shown(self, timeout: int = 10):
        """Ожидание отображения координат после клика"""
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(self.LAT_VALUE)
        )
        self.logger.info("Координаты отображены")

    def get_latitude_text(self) -> str:
        """Текст широты"""
        return " ".join(self.get_text(self.LAT_VALUE).split())

    def get_longitude_text(self) -> str:
        """Текст долготы"""
        return " ".join(self.get_text(self.LONG_VALUE).split())

    def get_maps_link_href(self) -> str:
        """Ссылка 'See it on Google Maps' (атрибут href)"""
        return self.get_attribute(self.MAPS_LINK, "href")

    def get_maps_link_text(self) -> str:
        """Текст ссылки на Google Maps"""
        return " ".join(self.get_text(self.MAPS_LINK).split())
