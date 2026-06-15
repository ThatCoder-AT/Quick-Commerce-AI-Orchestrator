from core.base_scraper import BaseScraper
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
import time

class BigBasketScraper(BaseScraper):
    def __init__(self, driver):
        super().__init__(driver)
        self.platform_name = "BigBasket"
        self.base_url = "https://www.bigbasket.com"
        self.tab_handle = None

    def search_item(self, query: str) -> list[dict]:
        results = []
        try:
            formatted_query = query.replace(" ", "+")
            self.driver.get(f"{self.base_url}/ps/?q={formatted_query}&nc=as")
            time.sleep(3.5) 
            
            add_buttons = self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//button[normalize-space(text())='Add']")
                )
            )[:5] 
            
            for index, btn in enumerate(add_buttons):
                try:
                    card = btn.find_element(By.XPATH, "./ancestor::div[.//img[@alt]][1]")
                    
                    try:
                        img_el = card.find_element(By.XPATH, ".//img[@alt]")
                        raw_name = img_el.get_attribute("alt").strip()
                    except Exception:
                        raw_name = "Unknown Product"
                    
                    raw_card_text = card.get_attribute("textContent").strip()
                    
                    results.append({
                        "platform": self.platform_name,
                        "raw_name": raw_name,
                        "raw_card_text": raw_card_text,
                        "cart_element": btn
                    })
                except Exception as e:
                    continue
                    
            print(f"[*] {self.platform_name} successfully extracted {len(results)} items.")
            return results
            
        except TimeoutException:
            print(f"[{self.platform_name}] Timeout waiting for element presence.")
            return []

    def add_to_cart(self, product_identifier) -> bool:
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", product_identifier)
            time.sleep(1)
            product_identifier.click()
            print(f"[{self.platform_name}] Successfully triggered cart injection.")
            return True
        except Exception as e:
            print(f"[-] [{self.platform_name}] Injection failed: {e}")
            return False