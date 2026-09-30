# -*- coding: utf-8 -*-
"""UI-тесты раздела Notification Messages (flash-уведомления)."""
import pytest
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from data.test_data import TestData


class TestNotificationMessages:
    """Тесты раздела Notification Messages"""

    @pytest.mark.smoke
    @pytest.mark.notifications
    def test_open_notification_messages_from_home(self, home_page, notification_messages_page):
        """Переход в раздел Notification Messages с главной страницы"""
        home_page.open_home_page()
        home_page.open_notification_messages()

        assert "notification_message" in home_page.driver.current_url
        assert notification_messages_page.get_heading_text() == "Notification Message"

    @pytest.mark.smoke
    @pytest.mark.notifications
    def test_notification_appears_after_click(self, notification_messages_page):
        """После клика 'Click here' отображается flash-уведомление"""
        notification_messages_page.open_notification_page()

        notification_messages_page.click_here()
        notification_messages_page.wait_flash_visible()

        assert notification_messages_page.is_flash_visible()

    @pytest.mark.notifications
    def test_notification_text_is_known(self, notification_messages_page):
        """Текст уведомления — один из ожидаемых вариантов сайта"""
        notification_messages_page.open_notification_page()

        notification_messages_page.click_here()
        notification_messages_page.wait_flash_visible()

        assert notification_messages_page.flash_text_is_known(), (
            f"Неожиданный текст уведомления: "
            f"'{notification_messages_page.get_flash_text()}'"
        )

    @pytest.mark.negative
    @pytest.mark.notifications
    def test_notification_can_be_closed(self, notification_messages_page):
        """Уведомление закрывается крестиком"""
        notification_messages_page.open_notification_page()
        notification_messages_page.wait_flash_visible()

        notification_messages_page.close_flash()

        WebDriverWait(notification_messages_page.driver, 10).until(
            EC.invisibility_of_element_located(notification_messages_page.FLASH)
        )
        assert not notification_messages_page.is_flash_visible()

    @pytest.mark.notifications
    def test_notification_reappears_on_each_click(self, notification_messages_page):
        """Каждый из нескольких кликов загружает новое уведомление"""
        notification_messages_page.open_notification_page()

        for click_number in range(3):
            notification_messages_page.click_here()
            notification_messages_page.wait_flash_visible()

            assert notification_messages_page.is_flash_visible(), (
                f"Уведомление не появилось после клика №{click_number + 1}"
            )
            assert notification_messages_page.flash_text_is_known()
