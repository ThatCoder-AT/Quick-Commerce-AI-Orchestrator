from abc import ABC, abstractmethod
from selenium.webdriver.support.ui import WebDriverWait

class BaseScraper(ABC):
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(self.driver, 10)
        self.platform_name = "Base"

    @abstractmethod
    def search_item(self, query: str) -> list[dict]:
        pass

    @abstractmethod
    def add_to_cart(self, product_identifier) -> bool:
        pass