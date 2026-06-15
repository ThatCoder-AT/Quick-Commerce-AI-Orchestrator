from core.base_scraper import BaseScraper
from utils import normalize_price
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import re
import time

class BlinkitScraper(BaseScraper):
    def __init__(self, driver):
        super().__init__(driver)
        self.platform_name = "Blinkit"
        self.base_url = "https://blinkit.com/"
        self.tab_handle = None

    def search_item(self, query: str) -> list[dict]:
        results = []
        try:
            formatted_query = query.replace(" ", "+")
            self.driver.get(f"{self.base_url}s/?q={formatted_query}")
            time.sleep(2.5) 
            
            add_buttons = self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "//div[@role='button' and contains(@class, 'tw-bg-green-050')]")
                )
            )[:5] 
            
            for btn in add_buttons:
                try:
                    card = btn.find_element(By.XPATH, "./ancestor::div[.//div[contains(@class, 'tw-line-clamp-2')]][1]")
                    
                    name = card.find_element(By.XPATH, ".//div[contains(@class, 'tw-line-clamp-2')]").get_attribute("textContent").strip()
                    
                    price_str = card.find_element(By.XPATH, ".//div[contains(@class, 'tw-text-200') and contains(text(), '₹')]").get_attribute("textContent").strip()
                    price = float(price_str.replace('₹', '').strip())
                    
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
                except Exception:
                    continue 
                    
            print(f"[*] {self.platform_name} successfully extracted {len(results)} items.")
            return results
            
        except TimeoutException:
            print(f"[{self.platform_name}] Timeout parsing visual layout objects.")
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