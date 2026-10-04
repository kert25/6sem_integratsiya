from appium.webdriver.common.appiumby import AppiumBy

from pages.base_page import BasePage


class SearchPage(BasePage):
    SEARCH_CONTAINER = (AppiumBy.ID, "org.wikipedia:id/nav_tab_search")
    SEARCH_WIDGET_PROMO_CLOSE = (AppiumBy.ACCESSIBILITY_ID, "Close")
    SEARCH_CARD = (AppiumBy.ID, "org.wikipedia:id/search_text_view")
    CLEAR_QUERY_BUTTON = (AppiumBy.ACCESSIBILITY_ID, "Clear query")
    SEARCH_INPUT = (AppiumBy.ID, "org.wikipedia:id/search_src_text")
    RESULT_TEXT = (AppiumBy.XPATH, "//*[@text]")

    def open(self) -> None:
        if self.is_visible(self.SEARCH_CONTAINER, timeout=2):
            self.click(self.SEARCH_CONTAINER)
        if self.is_visible(self.SEARCH_WIDGET_PROMO_CLOSE, timeout=2):
            self.click(self.SEARCH_WIDGET_PROMO_CLOSE)
        if self.is_visible(self.SEARCH_CARD, timeout=2):
            self.click(self.SEARCH_CARD)

    def search(self, query: str) -> None:
        field = self.wait_for_visibility(self.SEARCH_INPUT)
        field.clear()
        field.send_keys(query)

    def query_text(self) -> str:
        return self.wait_for_visibility(self.SEARCH_INPUT).text

    def clear_query(self) -> None:
        self.click(self.CLEAR_QUERY_BUTTON)
