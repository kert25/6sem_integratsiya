# -*- coding: utf-8 -*-
"""Page Object страницы Inputs (ввод числа)."""
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from .base_page import BasePage


class InputsPage(BasePage):
    """Страница раздела Inputs: единственное числовое поле"""

    # Локаторы (на странице Inputs заголовок h3 находится вне div.example)
    HEADING = (By.CSS_SELECTOR, "h3")
    NUMBER_INPUT = (By.CSS_SELECTOR, "input[type=number]")

    def open_inputs_page(self):
        """Открытие страницы Inputs напрямую"""
        self.open("inputs")

    def get_heading_text(self) -> str:
        """Текст заголовка страницы"""
        return self.get_text(self.HEADING)

    def enter_number(self, value: str):
        """Ввод значения в числовое поле (с предварительной очисткой)"""
        element = self.wait_for_element_visible(self.NUMBER_INPUT)
        element.clear()
        element.send_keys(value)
        self.logger.info(f"Введено значение: {value}")

    def get_input_value(self) -> str:
        """Текущее значение поля (атрибут value)"""
        return self.get_attribute(self.NUMBER_INPUT, "value")

    def clear_input(self):
        """Очистка поля"""
        element = self.wait_for_element_visible(self.NUMBER_INPUT)
        element.clear()
        self.logger.info("Поле очищено")

    def send_keys_to_input(self, *keys):
        """Отправка клавиш в поле (в т. ч. букв и служебных клавиш)"""
        element = self.wait_for_element_visible(self.NUMBER_INPUT)
        for key in keys:
            element.send_keys(key)
        self.logger.info(f"Отправлены клавиши: {keys}")

    def press_arrow_up(self, times: int = 1):
        """Нажатие стрелки вверх (увеличивает значение на 1)"""
        self.send_keys_to_input(*([Keys.ARROW_UP] * times))

    def press_arrow_down(self, times: int = 1):
        """Нажатие стрелки вниз (уменьшает значение на 1)"""
        self.send_keys_to_input(*([Keys.ARROW_DOWN] * times))
