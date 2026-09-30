# -*- coding: utf-8 -*-
"""UI-тесты раздела Inputs (ввод числа, очистка, стрелки)."""
import pytest
from data.test_data import TestData


class TestInputs:
    """Тесты раздела Inputs"""

    @pytest.mark.smoke
    @pytest.mark.inputs
    def test_open_inputs_from_home(self, home_page, inputs_page):
        """Переход в раздел Inputs с главной страницы"""
        home_page.open_home_page()
        home_page.open_inputs()

        assert "inputs" in home_page.driver.current_url
        assert inputs_page.get_heading_text() == "Inputs"

    @pytest.mark.smoke
    @pytest.mark.inputs
    def test_enter_number(self, inputs_page):
        """Ввод целого числа в поле"""
        inputs_page.open_inputs_page()

        inputs_page.enter_number(TestData.INPUT_NUMBER)

        assert inputs_page.get_input_value() == TestData.INPUT_NUMBER

    @pytest.mark.inputs
    def test_enter_decimal_number(self, inputs_page):
        """Ввод десятичного числа"""
        inputs_page.open_inputs_page()

        inputs_page.enter_number(TestData.DECIMAL_NUMBER)

        assert inputs_page.get_input_value() == TestData.DECIMAL_NUMBER

    @pytest.mark.inputs
    def test_enter_negative_number(self, inputs_page):
        """Ввод отрицательного числа"""
        inputs_page.open_inputs_page()

        inputs_page.enter_number(TestData.NEGATIVE_NUMBER)

        assert inputs_page.get_input_value() == TestData.NEGATIVE_NUMBER

    @pytest.mark.inputs
    def test_clear_input(self, inputs_page):
        """Очистка заполненного поля"""
        inputs_page.open_inputs_page()

        inputs_page.enter_number(TestData.INPUT_NUMBER)
        inputs_page.clear_input()

        assert inputs_page.get_input_value() == ""

    @pytest.mark.negative
    @pytest.mark.inputs
    def test_non_numeric_input_ignored(self, inputs_page):
        """Негативный: буквы в поле type=number не вводятся"""
        inputs_page.open_inputs_page()

        inputs_page.send_keys_to_input(TestData.NON_NUMERIC_INPUT)

        assert inputs_page.get_input_value() == ""

    @pytest.mark.inputs
    def test_arrow_keys_change_value(self, inputs_page):
        """Стрелки вверх/вниз изменяют значение на единицу"""
        inputs_page.open_inputs_page()

        inputs_page.press_arrow_up()
        assert inputs_page.get_input_value() == "1"

        inputs_page.press_arrow_up()
        assert inputs_page.get_input_value() == "2"

        inputs_page.press_arrow_down()
        assert inputs_page.get_input_value() == "1"
