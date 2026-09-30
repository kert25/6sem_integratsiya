# -*- coding: utf-8 -*-
"""Создание скриншотов страницы (в т. ч. при падении тестов)."""
import logging
import os
from datetime import datetime
from selenium.webdriver.remote.webdriver import WebDriver

logger = logging.getLogger(__name__)


class ScreenshotManager:
    """Менеджер скриншотов: сохраняет PNG в каталог screenshots/."""

    def __init__(self, driver: WebDriver, directory: str = "screenshots"):
        self.driver = driver
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)

    def take_screenshot(self, name: str = "screenshot") -> str:
        """Скриншот текущего состояния страницы."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.directory, f"{name}_{timestamp}.png")
        if self.driver.save_screenshot(filename):
            logger.info(f"Скриншот сохранен: {filename}")
            return filename
        logger.error(f"Не удалось сохранить скриншот: {filename}")
        return ""
