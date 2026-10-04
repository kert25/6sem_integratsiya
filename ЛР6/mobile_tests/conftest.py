from __future__ import annotations

from datetime import datetime

import pytest

from config import SCREENSHOTS_DIR
from pages.onboarding_page import OnboardingPage
from utils.driver_factory import create_android_driver


@pytest.fixture
def driver():
    instance = create_android_driver()
    instance.activate_app("org.wikipedia")
    yield instance
    instance.quit()


@pytest.fixture
def wikipedia_home(driver):
    OnboardingPage(driver).skip_if_displayed()
    return driver


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


@pytest.fixture(autouse=True)
def save_screenshot_on_failure(request, driver):
    yield
    report = getattr(request.node, "rep_call", None)
    if report and report.failed:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        path = SCREENSHOTS_DIR / f"{request.node.name}_{timestamp}.png"
        try:
            driver.get_screenshot_as_file(str(path))
        except Exception:
            return
        if path.exists():
            try:
                import allure

                allure.attach.file(str(path), name=path.stem, attachment_type=allure.attachment_type.PNG)
            except ImportError:
                pass
