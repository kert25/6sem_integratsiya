# -*- coding: utf-8 -*-
"""UI-тесты раздела Geolocation (определение координат)."""
import pytest
from data.test_data import TestData


class TestGeolocation:
    """Тесты раздела Geolocation"""

    @pytest.mark.smoke
    @pytest.mark.geolocation
    def test_open_geolocation_from_home(self, home_page, geolocation_page):
        """Переход в раздел Geolocation с главной страницы"""
        home_page.open_home_page()
        home_page.open_geolocation()

        assert "geolocation" in home_page.driver.current_url
        assert geolocation_page.get_heading_text() == "Geolocation"

    @pytest.mark.geolocation
    def test_initial_prompt_text(self, geolocation_page):
        """До клика отображается приглашение нажать кнопку"""
        geolocation_page.open_geolocation_page()

        assert "Click the button" in geolocation_page.get_demo_text()

    @pytest.mark.smoke
    @pytest.mark.geolocation
    def test_where_am_i_shows_mock_coordinates(self, geolocation_page):
        """Кнопка 'Where am I?' выводит подмененные координаты"""
        geolocation_page.open_geolocation_page()

        geolocation_page.mock_geolocation()
        geolocation_page.click_where_am_i()
        geolocation_page.wait_coordinates_shown()

        assert geolocation_page.get_latitude_text() == str(TestData.MOCK_LATITUDE)
        assert geolocation_page.get_longitude_text() == str(TestData.MOCK_LONGITUDE)

    @pytest.mark.geolocation
    def test_google_maps_link_contains_coordinates(self, geolocation_page):
        """Ссылка на Google Maps содержит подмененные координаты"""
        geolocation_page.open_geolocation_page()

        geolocation_page.mock_geolocation()
        geolocation_page.click_where_am_i()
        geolocation_page.wait_coordinates_shown()

        expected_query = f"q={TestData.MOCK_LATITUDE},{TestData.MOCK_LONGITUDE}"
        assert expected_query in geolocation_page.get_maps_link_href()
        assert "Google" in geolocation_page.get_maps_link_text()
