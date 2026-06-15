import re
from core.base_scraper import BaseScraper
from utils import normalize_price
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
import time

class InstamartScraper(BaseScraper):
    def __init__(self, driver):
        super().__init__(driver)
        self.platform_name = "Instamart"
        self.base_url = "https://www.swiggy.com/instamart"
        self.tab_handle = None

    def search_item(self, query: str) -> list[dict]:
        results = []
        
        for attempt in range(2):
            try:
                self.driver.get(f"{self.base_url}/search")
                time.sleep(2)
                
                search_input = self.wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//input[@type='search' or contains(@placeholder, 'Search')]"))
                )
                
                # Force click to gain focus
                search_input.click()
                time.sleep(0.3)
                
                search_input.send_keys(Keys.CONTROL + "a")
                search_input.send_keys(Keys.BACKSPACE)
                time.sleep(0.3)
                
                # Emulate human typing so React registers the state change
                for char in query:
                    search_input.send_keys(char)
                    time.sleep(0.05) 
                
                # Crucial wait for Instamart's internal debounce function
                time.sleep(0.8)
                
                # Standard Enter
                search_input.send_keys(Keys.ENTER)
                time.sleep(1)
                
                # Check if it loaded. If not, force a hardware-level Enter using ActionChains
                if "query=" not in self.driver.current_url:
                    print(f"[*] [Instamart] Standard Enter failed. Firing hardware ActionChain Enter...")
                    ActionChains(self.driver).send_keys(Keys.ENTER).perform()
                    time.sleep(1.5)
                
                # Fallback: Physically click the suggestion dropdown
                if "query=" not in self.driver.current_url:
                    try:
                        suggestion = self.driver.find_element(By.XPATH, "//button[contains(., 'Search for')]")
                        suggestion.click()
                        time.sleep(1.5)
                    except Exception:
                        pass
                
                add_buttons = self.wait.until(
                    EC.presence_of_all_elements_located(
                        (By.XPATH, "//div[@data-testid='buttonpair-add' or @aria-label='Add item to cart']")
                    )
                )[:5] 
                
                for index, btn in enumerate(add_buttons):
                    try:
                        card = btn.find_element(By.XPATH, "./ancestor::div[.//img[@alt]][1]")
                        
                        try:
                            img_el = card.find_element(By.XPATH, ".//img[@alt]")
                            name = img_el.get_attribute("alt").strip()
                        except Exception:
                            name = "Unknown Product"
                            
                        card_text = card.get_attribute("textContent")
                        
                        price = 0.0
                        price_match = re.search(r'(?:₹|Rs\.?)\s*(\d+(?:,\d+)*(?:\.\d{1,2})?)', card_text, re.IGNORECASE)
                        if price_match:
                            price = float(price_match.group(1).replace(',', ''))
                        else:
                            pure_number_divs = card.find_elements(By.XPATH, ".//div[string-length(normalize-space(text())) > 0 and not(translate(normalize-space(text()), '0123456789.,', ''))]")
                            if pure_number_divs:
                                price = float(pure_number_divs[0].get_attribute("textContent").replace(',', '').strip())
                        
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
                
            except (TimeoutException, StaleElementReferenceException):
                if attempt == 0:
                    print(f"[-] [Instamart] DOM timed out. Initiating self-healing refresh...")
                    continue 
                else:
                    print(f"[{self.platform_name}] Timeout after 2 attempts. No items found.")
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