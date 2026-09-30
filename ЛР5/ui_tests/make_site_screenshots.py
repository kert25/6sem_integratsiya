# -*- coding: utf-8 -*-
"""Скриншоты тестируемых страниц the-internet для отчёта (Selenium, headless)."""
import os
import sys

sys.path.insert(0, os.getcwd())

from utils.driver_manager import DriverManager
from pages.home_page import HomePage
from pages.inputs_page import InputsPage
from pages.notification_messages_page import NotificationMessagesPage
from pages.geolocation_page import GeolocationPage
from data.test_data import TestData

OUT = os.path.join("..", "screenshots")

dm = DriverManager(browser="chrome", headless=True)
driver = dm.create_driver()

try:
    home = HomePage(driver)
    home.open_home_page()
    driver.save_screenshot(os.path.join(OUT, "site_home.png"))

    inputs = InputsPage(driver)
    inputs.open_inputs_page()
    inputs.enter_number(TestData.INPUT_NUMBER)
    driver.save_screenshot(os.path.join(OUT, "site_inputs.png"))

    notif = NotificationMessagesPage(driver)
    notif.open_notification_page()
    notif.click_here()
    notif.wait_flash_visible()
    driver.save_screenshot(os.path.join(OUT, "site_notification.png"))

    geo = GeolocationPage(driver)
    geo.open_geolocation_page()
    geo.mock_geolocation()
    geo.click_where_am_i()
    geo.wait_coordinates_shown()
    driver.save_screenshot(os.path.join(OUT, "site_geolocation.png"))
finally:
    dm.quit_driver()

print("done:", sorted(f for f in os.listdir(OUT) if f.startswith("site_")))
