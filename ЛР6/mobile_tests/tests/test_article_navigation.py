import allure

from pages.search_page import SearchPage


@allure.epic("Wikipedia Android")
@allure.feature("Навигация и поиск")
class TestSearchNavigation:
    @allure.title("TC-WIKI-02: введённый запрос можно очистить")
    def test_clear_search_query(self, wikipedia_home):
        search = SearchPage(wikipedia_home)

        search.open()
        search.search("Python")
        search.clear_query()

        assert search.query_text() == "Search Wikipedia"
