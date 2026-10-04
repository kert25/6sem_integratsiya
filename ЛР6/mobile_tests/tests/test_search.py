import allure

from pages.search_page import SearchPage


@allure.epic("Wikipedia Android")
@allure.feature("Поиск статей")
class TestWikipediaSearch:
    @allure.title("TC-WIKI-01: поисковый запрос вводится в поле Wikipedia")
    def test_search_query_is_entered(self, wikipedia_home):
        search = SearchPage(wikipedia_home)

        search.open()
        search.search("Python")

        assert search.query_text() == "Python"
