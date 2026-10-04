from __future__ import annotations

from pathlib import Path

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as conditions
from selenium.webdriver.support.ui import WebDriverWait

from config import DEFAULT_TIMEOUT


class BasePage:
    def __init__(self, driver, timeout: int = DEFAULT_TIMEOUT):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def find_element(self, locator):
        return self.wait.until(conditions.presence_of_element_located(locator))

    def wait_for_visibility(self, locator):
        return self.wait.until(conditions.visibility_of_element_located(locator))

    def wait_for_clickable(self, locator):
        return self.wait.until(conditions.element_to_be_clickable(locator))

    def click(self, locator) -> None:
        self.wait_for_clickable(locator).click()

    def is_visible(self, locator, timeout: int = 3) -> bool:
        try:
            WebDriverWait(self.driver, timeout).until(
                conditions.visibility_of_element_located(locator)
            )
        except TimeoutException:
            return False
        return True

    def take_screenshot(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.driver.get_screenshot_as_file(str(path))
        return path
