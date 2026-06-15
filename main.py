print("\n[*] Booting ThatCoder! Q-Comm AI Orchestrator... (Please wait)")

import undetected_chromedriver as uc
from tabulate import tabulate
import telebot
import config
import time
import json
import requests
import os
import socket
import subprocess
import re
import sys
from datetime import datetime
import customtkinter as ctk

from scrapers.blinkit import BlinkitScraper
from scrapers.zepto import ZeptoScraper
from scrapers.instamart import InstamartScraper
from scrapers.jiomart import JioMartScraper
from scrapers.bigbasket import BigBasketScraper

# ==========================================
# CONFIGURATION & SECRETS
# ==========================================
OLLAMA_BASE_URL = "http://127.0.0.1:11434"
OLLAMA_ENDPOINT = f"{OLLAMA_BASE_URL}/api/generate"
OLLAMA_MODEL = "" 
HEADLESS_MODE = True # Default, overridden by GUI

# ⚠️ SECURITY: Never commit your actual token to GitHub!
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_HERE")

bot = telebot.TeleBot(BOT_TOKEN)

# ==========================================
# BOOT AND GUI LOGIC
# ==========================================
def boot_ollama_server():
    """Ensures the Ollama daemon is running in the background."""
    print("[*] Verifying Ollama daemon status...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1.0) 
        if s.connect_ex(('127.0.0.1', 11434)) == 0: 
            print("[+] Local LLM server is already running.")
            return

    print("[*] Ollama server is offline. Booting via 'ollama serve'...")
    if sys.platform == "win32":
        DETACHED_PROCESS = 0x00000008
        subprocess.Popen("ollama serve", shell=True, creationflags=DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP, close_fds=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        subprocess.Popen("ollama serve", shell=True, start_new_session=True, close_fds=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    for _ in range(15):
        time.sleep(1)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as check_sock:
            check_sock.settimeout(1.0)
            if check_sock.connect_ex(('127.0.0.1', 11434)) == 0:
                print("[+] Local LLM server is now live!")
                return
    print("[-] Warning: Could not verify server startup. GUI may not load models.")

def get_installed_models():
    """Fetches installed models using the hyper-reliable REST API."""
    print("[*] Querying Ollama API for installed models...")
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        response.raise_for_status()
        models_data = response.json().get("models", [])
        models = [m["name"] for m in models_data]
        return models if models else ["No models found (Install one?)"]
    except requests.exceptions.RequestException as e:
        print(f"[-] API Error while fetching models: {e}")
        return ["No models found (Is Ollama installed?)"]

def setup_gui():
    """Builds a sleek, modern UI to select the Ollama model and browser mode."""
    global OLLAMA_MODEL, HEADLESS_MODE
    
    print("[*] Drawing Graphical Interface...")
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("ThatCoder! Q-Comm AI")
    root.geometry("550x420") # Expanded slightly for the new checkbox
    
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width / 2) - (550 / 2)
    y = (screen_height / 2) - (420 / 2)
    root.geometry(f'+{int(x)}+{int(y)}')

    root.attributes('-topmost', True)
    root.update()
    root.attributes('-topmost', False)

    models = get_installed_models()
    selected_model = ctk.StringVar(value=models[0])
    
    # Checkbox Variable
    headless_var = ctk.BooleanVar(value=True)

    title = ctk.CTkLabel(root, text="🤖 Q-Comm AI Orchestrator", font=ctk.CTkFont(size=26, weight="bold"), text_color="#38bdf8")
    title.pack(pady=(40, 10))

    subtitle = ctk.CTkLabel(root, text="Select Local LLM Brain:", font=ctk.CTkFont(size=14))
    subtitle.pack(pady=(10, 5))

    combo = ctk.CTkComboBox(root, variable=selected_model, values=models, width=300, height=35, font=ctk.CTkFont(size=14), dropdown_font=ctk.CTkFont(size=13))
    combo.pack(pady=10)

    # Browser Mode Toggle
    checkbox = ctk.CTkCheckBox(root, text="Run in Stealth (Headless) Mode", variable=headless_var, font=ctk.CTkFont(size=13), border_color="#3b82f6", fg_color="#3b82f6")
    checkbox.pack(pady=15)

    def on_start():
        global OLLAMA_MODEL, HEADLESS_MODE
        selection = selected_model.get()
        if "No models found" in selection:
            return 
        OLLAMA_MODEL = selection
        HEADLESS_MODE = headless_var.get()
        root.destroy()

    btn = ctk.CTkButton(root, text="Initialize Engine & Start Bot", command=on_start, width=250, height=45, font=ctk.CTkFont(size=15, weight="bold"))
    btn.pack(pady=20)
    
    root.mainloop()

def preload_model():
    """Explicitly loads the chosen model into VRAM."""
    print(f"[*] Pre-loading '{OLLAMA_MODEL}' into VRAM. This might take a few seconds...")
    try:
        requests.post(OLLAMA_ENDPOINT, json={"model": OLLAMA_MODEL, "prompt": "Initialize.", "stream": False, "options": {"num_predict": 2}}, timeout=60)
        print("[+] AI Engine is locked and loaded!")
    except Exception as e:
        print(f"[-] Note: Could not pre-load model via API. Error: {e}")

# ==========================================
# AGENT LOGIC
# ==========================================
def query_ollama(user_query: str, items_json: str) -> dict:
    prompt = f"""
    You are an elite grocery shopping AI. The user wants to buy: "{user_query}"
    
    Below is a JSON list of products scraped from different websites. 
    Your job is to find the single best item.
    
    RULES:
    1. The item must match the requested brand.
    2. The price must be greater than 0.
    3. Pick the cheapest valid item.
    4. Calculate the normalized price (e.g., "₹50 per kg").
    
    PRODUCTS DATA:
    {items_json}
    
    You MUST respond with a JSON block. Do not output an empty JSON {{}}.
    Use this EXACT format for your response:
    ```json
    {{
        "winner_id": "item_X",
        "price": 27.0,
        "quantity_extracted": "1 kg",
        "normalized_price": "₹27.0 per kg",
        "reason": "Exact match and lowest price."
    }}
    ```
    """
    try:
        response = requests.post(OLLAMA_ENDPOINT, json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.1, "num_ctx": 8192}
        }, timeout=120) 
        response.raise_for_status()
        
        raw_response = response.json().get("response", "").strip()
        json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
        
        if json_match:
            parsed = json.loads(json_match.group(0))
            return parsed if parsed else None
        return None
    except Exception:
        return None

def setup_driver():
    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={config.USER_DATA_DIR}")
    options.add_argument(f"--profile-directory={config.PROFILE_DIRECTORY}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Use the dynamic GUI selection for headless mode
    driver = uc.Chrome(options=options, headless=HEADLESS_MODE)
    driver.maximize_window()
    return driver

def update_tg_status(chat_id, msg_id, text):
    try:
        bot.edit_message_text(chat_id=chat_id, message_id=msg_id, text=text, parse_mode="Markdown")
    except Exception:
        pass

def generate_html_receipt(report_data, filename):
    total_sum = 0.0
    html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>ThatCoder! Auto-Shopper Receipt</title>
        <style>
            body { font-family: 'Segoe UI', system-ui, sans-serif; background-color: #f1f5f9; padding: 40px; color: #0f172a; margin: 0; }
            .container { max-width: 900px; margin: 0 auto; background: white; padding: 40px; border-radius: 16px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); }
            h1 { color: #2563eb; text-align: center; margin-bottom: 5px; font-size: 2.5em; }
            p.subtitle { text-align: center; color: #64748b; font-size: 1.1em; border-bottom: 2px dashed #cbd5e1; padding-bottom: 30px; margin-bottom: 30px; }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 16px; text-align: left; border-bottom: 1px solid #e2e8f0; }
            th { background-color: #f8fafc; font-weight: 700; color: #475569; font-size: 0.95em; text-transform: uppercase; letter-spacing: 0.5px; }
            tr:hover { background-color: #f8fafc; }
            .success { color: #059669; font-weight: bold; background: #d1fae5; padding: 4px 8px; border-radius: 6px; font-size: 0.9em; }
            .failed { color: #e11d48; font-weight: bold; background: #ffe4e6; padding: 4px 8px; border-radius: 6px; font-size: 0.9em; }
            .price { font-weight: 800; color: #0f172a; font-size: 1.1em; }
            .platform { font-weight: 600; color: #3b82f6; }
            .footer { text-align: center; margin-top: 40px; color: #94a3b8; font-size: 0.9em; }
            tfoot tr td { font-size: 1.2em; font-weight: bold; padding-top: 20px; }
            tfoot tr td.total-label { color: #475569; text-align: right; }
            tfoot tr td.total-value { color: #059669; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🧾 Shopping Receipt</h1>
            <p class="subtitle">Generated autonomously by ThatCoder! AI Engine</p>
            <table>
                <thead>
                    <tr>
                        <th>Item Requested</th>
                        <th>Status</th>
                        <th>Platform</th>
                        <th>Product Match</th>
                        <th>Price</th>
                        <th>Norm. Price</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for row in report_data:
        status_badge = "success" if row[1] == "SUCCESS" else "failed"
        if row[1] == "SUCCESS":
            try:
                price_val = float(str(row[4]).replace('₹', '').replace(',', '').strip())
                total_sum += price_val
            except Exception:
                pass

        html += f"""
                    <tr>
                        <td style="font-weight: 600;">{row[0]}</td>
                        <td><span class="{status_badge}">{row[1]}</span></td>
                        <td class="platform">{row[2]}</td>
                        <td style="color: #475569;">{row[3]}</td>
                        <td class="price">{row[4]}</td>
                        <td style="color: #64748b;">{row[5]}</td>
                    </tr>
        """
        
    html += f"""
                </tbody>
                <tfoot>
                    <tr style="border-top: 2px solid #cbd5e1; background-color: transparent;">
                        <td colspan="4" class="total-label">Grand Total Estimated:</td>
                        <td colspan="2" class="total-value">₹{total_sum:.2f}</td>
                    </tr>
                </tfoot>
            </table>
            <div class="footer">Thank you for using the Q-Comm AI Orchestrator.</div>
        </div>
    </body>
    </html>
    """
    with open(filename, "w", encoding="utf-8") as f:
        f.write(html)
    return filename

def run_shopping_agent(shopping_list, chat_id, status_msg_id):
    driver = setup_driver()
    scrapers_classes = [BlinkitScraper, ZeptoScraper, InstamartScraper, JioMartScraper, BigBasketScraper]
    scrapers = []
    
    main_handle = driver.current_window_handle
    for idx, cls in enumerate(scrapers_classes):
        if idx == 0:
            scraper_instance = cls(driver)
            scraper_instance.tab_handle = main_handle
        else:
            driver.switch_to.new_window('tab')
            new_handle = driver.current_window_handle
            scraper_instance = cls(driver)
            scraper_instance.tab_handle = new_handle
        scrapers.append(scraper_instance)
        
    final_report = []
    completed_log = [] 
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    receipt_filename = f"shopping_receipt_{timestamp}.html"

    try:
        for query in shopping_list:
            all_raw_results = []
            interaction_map = {}
            
            for scraper in scrapers:
                live_text = "🛒 **LIVE SHOPPING TRACKER**\n\n"
                if completed_log:
                    live_text += "\n".join(completed_log) + "\n\n"
                live_text += f"🔄 **Hunting:** `{query.upper()}`\n  └ 🕵️ Scanning *{scraper.platform_name}*..."
                update_tg_status(chat_id, status_msg_id, live_text)
                print(f"[*] Extracting data from {scraper.platform_name}...")
                
                driver.switch_to.window(scraper.tab_handle)
                try:
                    results = scraper.search_item(query)
                    for r in results:
                        r['scraper_reference'] = scraper
                    all_raw_results.extend(results)
                except Exception:
                    pass
                
            if not all_raw_results:
                final_report.append([query, "FAILED", "Not Found", "-", "-", "-"])
                completed_log.append(f"❌ `{query}` -> Not Found")
                continue

            llm_payload = {"user_search_query": query, "scraped_items": []}
            for idx, item in enumerate(all_raw_results):
                item_id = f"item_{idx}"
                raw_text = item.get('raw_card_text', f"Price: {item.get('price', 0.0)} Qty: {item.get('quantity', '-')}")
                clean_card_text = re.sub(r'\s+', ' ', str(raw_text)).strip()[:250]
                
                interaction_map[item_id] = {
                    "scraper": item['scraper_reference'],
                    "cart_element": item['cart_element'],
                    "platform": item['platform'],
                    "name": item.get('name', item.get('raw_name')),
                    "fallback_price": item.get('price', 0.0)
                }
                llm_payload["scraped_items"].append({
                    "item_id": item_id,
                    "platform": item['platform'],
                    "extracted_title": item.get('name', item.get('raw_name')),
                    "raw_card_text": clean_card_text
                })

            live_text = "🛒 **LIVE SHOPPING TRACKER**\n\n"
            if completed_log:
                live_text += "\n".join(completed_log) + "\n\n"
            live_text += f"🔄 **Hunting:** `{query.upper()}`\n  └ 🧠 *{OLLAMA_MODEL}* evaluating {len(all_raw_results)} items..."
            update_tg_status(chat_id, status_msg_id, live_text)

            json_payload = json.dumps(llm_payload, indent=2)
            llm_decision = query_ollama(query, json_payload)
            
            if llm_decision and "winner_id" in llm_decision:
                chosen_id = llm_decision["winner_id"]
                reported_price = llm_decision.get("price", interaction_map.get(chosen_id, {}).get("fallback_price", 0.0))
                norm_price = llm_decision.get("normalized_price", "-")
                qty_ext = llm_decision.get("quantity_extracted", "-")
                
                if chosen_id in interaction_map:
                    winner = interaction_map[chosen_id]
                    
                    driver.switch_to.window(winner["scraper"].tab_handle)
                    time.sleep(0.5)
                    success = winner["scraper"].add_to_cart(winner["cart_element"])
                    
                    if success:
                        final_report.append([query, "SUCCESS", winner['platform'], winner['name'][:30], f"₹{reported_price}", norm_price, qty_ext])
                        completed_log.append(f"✅ `{query}` -> Added to *{winner['platform']}* (₹{reported_price})")
                    else:
                        final_report.append([query, "FAILED", winner['platform'], "Click Failed", f"₹{reported_price}", norm_price, qty_ext])
                        completed_log.append(f"❌ `{query}` -> Found on {winner['platform']}, but failed to click Cart.")
                else:
                    final_report.append([query, "FAILED", "LLM Error", "Invalid ID", "-", "-", "-"])
                    completed_log.append(f"❌ `{query}` -> LLM Hallucinated ID")
            else:
                final_report.append([query, "FAILED", "LLM Error", "Malformed JSON", "-", "-", "-"])
                completed_log.append(f"❌ `{query}` -> LLM Parsing Error")

        live_text = "🛒 **SHOPPING COMPLETE!**\n\n" + "\n".join(completed_log)
        update_tg_status(chat_id, status_msg_id, live_text)

        return generate_html_receipt(final_report, receipt_filename)
                
    finally:
        print("[*] Shopping trip concluded. Tearing down stealth browser...")
        driver.quit()

# ==========================================
# TELEGRAM BOT HANDLERS
# ==========================================
@bot.message_handler(commands=['start'])
def send_welcome(message):
    help_text = (
        "🤖 **Welcome to ThatCoder! Auto-Shopper**\n\n"
        "Send me a list of groceries (one per line). I will autonomously scan Blinkit, Zepto, Instamart, JioMart, and BigBasket, "
        "use my local LLM to do the math, and add the absolute cheapest items directly to your cart.\n\n"
        "*Example:*\nTata Salt\nAriel Liquid Top Load\nAmul Taaza Milk"
    )
    bot.reply_to(message, help_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def process_telegram_list(message):
    shopping_list = [line.strip() for line in message.text.split('\n') if line.strip()]
    if not shopping_list:
        return
        
    status_msg = bot.reply_to(message, "🚀 **Stealth Browser Initialized!**\n⏳ Preparing to hunt...", parse_mode="Markdown")
        
    try:
        receipt_path = run_shopping_agent(shopping_list, message.chat.id, status_msg.message_id)
        
        if os.path.exists(receipt_path):
            with open(receipt_path, "rb") as doc:
                bot.send_document(message.chat.id, doc, caption="🧾 **Mission Accomplished.**\nHere is your beautifully styled HTML receipt! Open it in any web browser.", parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, "⚠️ Script finished, but no log file was generated.")
    except Exception as e:
        bot.edit_message_text(chat_id=message.chat.id, message_id=status_msg.message_id, text=f"❌ **Engine crashed:**\n`{e}`", parse_mode="Markdown")

if __name__ == "__main__":
    boot_ollama_server() 
    setup_gui() 
    
    if OLLAMA_MODEL and "No models" not in OLLAMA_MODEL: 
        mode_str = "Stealth (Headless)" if HEADLESS_MODE else "Visible (Debug)"
        print(f"\n[*] Unified Q-Comm Engine Online.")
        print(f"[*] Brain: {OLLAMA_MODEL} | Browser Mode: {mode_str}")
        preload_model()
        print("[*] Telegram Bot is actively listening for messages...")
        bot.infinity_polling()
    else:
        print("\n[-] Setup aborted or no valid model selected. Exiting application.")