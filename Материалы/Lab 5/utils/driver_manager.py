"""
Управление веб-драйвером
"""
import logging
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager

logger = logging.getLogger(__name__)


class DriverManager:
    """Класс для управления веб-драйвером"""
    
    def __init__(self, browser: str = "chrome", headless: bool = False):
        self.browser = browser.lower()
        self.headless = headless
        self.driver: Optional[webdriver.Remote] = None
    
    def create_driver(self) -> webdriver.Remote:
        """Создание экземпляра веб-драйвера"""
        logger.info(f"Создание драйвера для браузера: {self.browser}")
        
        if self.browser == "chrome":
            options = webdriver.ChromeOptions()
            if self.headless:
                options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-notifications")
            options.add_experimental_option("excludeSwitches", ["enable-logging"])
            
            service = ChromeService(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
        
        elif self.browser == "firefox":
            options = webdriver.FirefoxOptions()
            if self.headless:
                options.add_argument("--headless")
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")
            
            service = FirefoxService(GeckoDriverManager().install())
            self.driver = webdriver.Firefox(service=service, options=options)
        
        elif self.browser == "edge":
            options = webdriver.EdgeOptions()
            if self.headless:
                options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            
            service = EdgeService(EdgeChromiumDriverManager().install())
            self.driver = webdriver.Edge(service=service, options=options)
        
        else:
            raise ValueError(f"Неподдерживаемый браузер: {self.browser}")
        
        # Настройки драйвера
        self.driver.implicitly_wait(10)  # Неявное ожидание
        self.driver.maximize_window()
        
        logger.info(f"Драйвер создан: {self.driver}")
        return self.driver
    
    def quit_driver(self):
        """Закрытие драйвера"""
        if self.driver:
            logger.info("Закрытие драйвера")
            self.driver.quit()
            self.driver = None
    
    def take_screenshot(self, filename: str = "screenshot.png"):
        """Создание скриншота текущей страницы"""
        if self.driver:
            self.driver.save_screenshot(filename)
            logger.info(f"Скриншот сохранен: {filename}")
            return filename
        return None
