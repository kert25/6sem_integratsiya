from appium.webdriver.common.appiumby import AppiumBy

from pages.base_page import BasePage


class ArticlePage(BasePage):
    VISIBLE_TEXT = (AppiumBy.XPATH, "//*[@text]")

    def title_contains(self, expected_title: str) -> bool:
        return any(
            expected_title.casefold() in element.text.casefold()
            for element in self.driver.find_elements(*self.VISIBLE_TEXT)
        )
