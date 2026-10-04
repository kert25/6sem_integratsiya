from __future__ import annotations

from appium import webdriver
from appium.options.android import UiAutomator2Options

from config import (
    APPIUM_URL,
    APP_ACTIVITY,
    APP_PACKAGE,
    APP_PATH,
    DEVICE_NAME,
    PLATFORM_VERSION,
    UDID,
)


def create_android_driver():
    """Создаёт сессию UiAutomator2 для установленного Wikipedia."""
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = DEVICE_NAME
    options.app_package = APP_PACKAGE
    options.app_activity = APP_ACTIVITY
    options.no_reset = True
    options.auto_grant_permissions = True
    options.new_command_timeout = 120

    if PLATFORM_VERSION:
        options.platform_version = PLATFORM_VERSION
    if UDID:
        options.udid = UDID
    if APP_PATH:
        options.app = APP_PATH

    return webdriver.Remote(APPIUM_URL, options=options)
