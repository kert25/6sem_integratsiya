from __future__ import annotations

import os
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
REPORTS_DIR = PROJECT_DIR / "reports"
SCREENSHOTS_DIR = REPORTS_DIR / "failure_screenshots"

APPIUM_URL = os.getenv("APPIUM_URL", "http://127.0.0.1:4723")
DEVICE_NAME = os.getenv("ANDROID_DEVICE_NAME", "LR6_Pixel_6")
PLATFORM_VERSION = os.getenv("ANDROID_PLATFORM_VERSION")
UDID = os.getenv("ANDROID_UDID")
APP_PATH = os.getenv("WIKIPEDIA_APK")

APP_PACKAGE = "org.wikipedia"
APP_ACTIVITY = "org.wikipedia.main.MainActivity"
DEFAULT_TIMEOUT = 15
