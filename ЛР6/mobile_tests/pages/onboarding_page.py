from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException

from pages.base_page import BasePage


class OnboardingPage(BasePage):
    SKIP_BUTTON = (AppiumBy.ID, "org.wikipedia:id/fragment_onboarding_skip_button")
    FORWARD_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "Forward")
    NEXT_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "Next")
    SKIP_TEXT = (AppiumBy.XPATH, "//*[@text='Skip']")

    def skip_if_displayed(self) -> None:
        for locator in (self.SKIP_BUTTON, self.SKIP_TEXT):
            try:
                self.driver.find_element(*locator).click()
                return
            except NoSuchElementException:
                pass

        for _ in range(6):
            for locator in (self.FORWARD_BUTTON, self.NEXT_BUTTON):
                if self.is_visible(locator, timeout=3):
                    self.click(locator)
                    break
            else:
                return
