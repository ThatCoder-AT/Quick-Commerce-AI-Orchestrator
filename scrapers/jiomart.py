import re
from core.base_scraper import BaseScraper
from utils import normalize_price
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
import time

class JioMartScraper(BaseScraper):
    def __init__(self, driver):
        super().__init__(driver)
        self.platform_name = "JioMart"
        self.base_url = "https://www.jiomart.com/"
        self.tab_handle = None

    def search_item(self, query: str) -> list[dict]:
        results = []
        try:
            self.driver.get(self.base_url)
            
            # Instantly wait for and trigger the search bar
            search_input = self.wait.until(
                EC.element_to_be_clickable((By.XPATH, "//input[@type='text' and (contains(@placeholder, 'Search') or contains(@class, 'SearchInput'))]"))
            )
            search_input.send_keys(Keys.CONTROL + "a")
            search_input.send_keys(Keys.DELETE)
            search_input.send_keys(query)
            search_input.send_keys(Keys.RETURN)
            
            # Instantly wait for the layout to hydrate
            titles = self.wait.until(
                EC.presence_of_all_elements_located((By.XPATH, "//*[contains(@class, 'productCard__productTitle') or contains(@class, 'productTitle')]"))
            )[:5] 
            
            for index, title_el in enumerate(titles):
                try:
                    card = title_el.find_element(By.XPATH, "./ancestor::*[.//button][1]")
                    name = title_el.get_attribute("textContent").strip()
                    
                    price_el = card.find_element(By.XPATH, ".//*[contains(@class, 'PriceContainer__currentPrice')]")
                    price_str = price_el.get_attribute("textContent").strip()
                    price_match = re.search(r'[\d.]+', price_str.replace(',', ''))
                    price = float(price_match.group()) if price_match else 0.0
                    
                    card_text = card.get_attribute("textContent")
                    qty_match = re.search(r'(\d+(?:\.\d+)?\s*(?:kg|g|l|ml|ltr|litre))', card_text, re.IGNORECASE)
                    qty = qty_match.group(1).strip() if qty_match else "1 unit"
                        
                    btn = card.find_element(By.XPATH, ".//button")
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
                except Exception:
                    continue
                    
            print(f"[*] {self.platform_name} successfully extracted {len(results)} items.")
            return results
            
        except TimeoutException:
            print(f"[{self.platform_name}] Timeout waiting for element presence.")
            return []

    def add_to_cart(self, product_identifier) -> bool:
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", product_identifier)
            time.sleep(1) # Keeping this 1s sleep ensures the scrolling animation finishes before clicking
            product_identifier.click()
            print(f"[{self.platform_name}] Successfully triggered cart injection.")
            return True
        except Exception as e:
            print(f"[-] [{self.platform_name}] Injection tracking action failed: {e}")
            return False