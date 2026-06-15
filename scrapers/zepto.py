import re
from core.base_scraper import BaseScraper
from utils import normalize_price
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

class ZeptoScraper(BaseScraper):
    def __init__(self, driver):
        super().__init__(driver)
        self.platform_name = "Zepto"
        self.base_url = "https://www.zeptonow.com/"
        self.tab_handle = None

    def search_item(self, query: str) -> list[dict]:
        results = []
        try:
            formatted_query = query.replace(" ", "+")
            self.driver.get(f"{self.base_url}search?query={formatted_query}")
            time.sleep(2.5)
            
            add_buttons = self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//button[normalize-space(text())='ADD']")
                )
            )[:5] 
            
            for index, btn in enumerate(add_buttons):
                try:
                    card = btn.find_element(By.XPATH, "./ancestor::*[.//div[@data-slot-id='ProductName']][1]")
                    
                    name_el = card.find_element(By.XPATH, ".//div[@data-slot-id='ProductName']")
                    name = name_el.get_attribute("textContent").strip()
                    if not name:
                        name = "Unknown Product"
                    
                    price_str = card.find_element(By.XPATH, ".//*[contains(text(), '₹')]").get_attribute("textContent").strip()
                    price_match = re.search(r'[\d.]+', price_str.replace(',', ''))
                    price = float(price_match.group()) if price_match else 0.0
                    
                    card_text = card.get_attribute("textContent")
                    qty_match = re.search(r'(\d+(?:\.\d+)?\s*(?:kg|g|l|ml|ltr|litre))', card_text, re.IGNORECASE)
                    qty = qty_match.group(1).strip() if qty_match else "1 unit"
                        
                    brand = query.split()[0] if query.split() else "Unknown"

                    results.append({
                        "platform": self.platform_name,
                        "name": name,
                        "brand": brand,
                        "quantity": qty,
                        "price": price,
                        "normalized_price": normalize_price(price, qty),
                        "cart_element": btn
                    })
                except Exception as e:
                    continue
                    
            print(f"[*] Zepto successfully extracted {len(results)} items.")
            return results
            
        except TimeoutException:
            print(f"[{self.platform_name}] Timeout while searching.")
            return []

    def add_to_cart(self, product_identifier) -> bool:
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", product_identifier)
            time.sleep(1)
            product_identifier.click()
            print(f"[{self.platform_name}] Successfully clicked ADD.")
            return True
        except Exception as e:
            print(f"[{self.platform_name}] Failed to click ADD: {e}")
            return False