# 🛒 Quick Commerce AI Orchestrator

> Autonomous AI-powered grocery shopping agent for India’s Quick Commerce ecosystem.

An intelligent full-stack automation engine that integrates with Telegram, local Large Language Models (Ollama), and persistent browser sessions to automatically search, compare, evaluate, and add grocery products to carts across multiple platforms.

The system continuously scans leading Indian quick-commerce providers, normalizes product pricing, verifies brand authenticity, and automatically selects the most cost-effective option with zero manual intervention.

---

## 🚀 Supported Platforms

* Blinkit
* Zepto
* Swiggy Instamart
* JioMart
* BigBasket

---

## ✨ Features

### 🤖 AI-Powered Product Selection

Uses locally hosted LLMs through Ollama to:

* Analyze unstructured product listings
* Ignore sponsored placements
* Detect fake or misleading matches
* Verify brand accuracy
* Compare package sizes
* Normalize pricing per Kg/Litre
* Select the mathematically cheapest genuine option

### 🛍 Multi-Platform Search Engine

Simultaneously searches:

* Blinkit
* Zepto
* Instamart
* JioMart
* BigBasket

using persistent browser sessions.

### 🕵️ Stealth Browser Automation

Built on:

* Selenium
* Undetected ChromeDriver
* Human-like interaction patterns
* ActionChains keyboard simulation

Designed to reduce automation detection.

### 🔄 Self-Healing DOM Engine

Handles:

* React SPA page updates
* DOM refreshes
* Detached elements
* Dynamic loading failures

Automatically retries and re-syncs when necessary.

### ➕ Automatic Cart Injection

After AI evaluation:

* Scrolls to winning product
* Clicks Add to Cart
* Maintains platform-specific cart state

### 💻 Modern Desktop GUI

Built with `customtkinter`.

Features:

* Dark Mode UI
* Ollama model selector
* Automatic model discovery
* Headless/Visual browser toggle
* One-click startup

### 📱 Telegram Integration

Send a grocery list directly to your Telegram bot.

The system:

* Updates a single message dynamically
* Shows live progress
* Avoids chat spam
* Provides final results automatically

### 🧾 Beautiful HTML Receipts

Generates detailed invoices containing:

* Product selections
* Platform source
* Normalized pricing
* Quantity information
* Estimated grand total
* Purchase summary

---

# 🏗 System Architecture

```text
┌─────────────────────┐
│ Telegram User       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Telegram Listener   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ Main Orchestrator   │
└──────────┬──────────┘
           │
           ├──────────────────────┐
           │                      │
           ▼                      ▼
┌─────────────────┐      ┌─────────────────┐
│ Browser Engine  │      │ Ollama LLM      │
│ (5 Active Tabs) │      │ Evaluation      │
└────────┬────────┘      └────────┬────────┘
         │                        │
         ▼                        ▼
┌──────────────────────────────────────┐
│ Product Scoring & Price Normalization│
└──────────────────┬───────────────────┘
                   │
                   ▼
┌─────────────────────┐
│ Cart Injection      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ HTML Receipt        │
└─────────────────────┘
```

---

# ⚙️ Prerequisites

Before installation ensure you have:

## 1. Python

Python 3.10 or newer.

Download:

https://www.python.org/downloads

---

## 2. Google Chrome

Install latest Chrome version.

https://www.google.com/chrome

---

## 3. Ollama

Install Ollama:

https://ollama.com

Verify installation:

```bash
ollama list
```

Download/Run at least one model:

```bash
ollama run gemma4:e2b
```

Example supported models:

```bash
gemma4:e4b
gemma4:12b
llama3
mistral
qwen3
```

---

## 4. Telegram Bot

Create a Telegram bot using:

https://t.me/BotFather

Save your Bot Token.

---

# 📦 Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/qcomm-ai-orchestrator.git

cd qcomm-ai-orchestrator
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🔑 Create Persistent Chrome Profile

This step is required so the automation can access your real shopping accounts.

Launch Chrome with a dedicated profile.

### Windows PowerShell

```powershell
& "C:\Program Files\Google\Chrome\Application\chrome.exe" `
--user-data-dir="C:\QCommProfile"
```

---

### Login Once To

* Blinkit
* Zepto
* Instamart
* JioMart
* BigBasket

After successful login:

1. Close Chrome completely
2. Keep the profile folder intact

The bot will reuse these authenticated sessions.

---

# ⚙️ Configuration

Create:

```python
# config.py

USER_DATA_DIR = r"C:\QCommProfile"
PROFILE_DIRECTORY = "Default"
```

---

## Telegram Configuration

Open:

```python
main.py
```

Replace:

```python
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
```

or use environment variables:

```bash
export TELEGRAM_BOT_TOKEN=YOUR_TOKEN
```

Windows:

```powershell
set TELEGRAM_BOT_TOKEN=YOUR_TOKEN
```

---

# 🚀 Running The System

Start Ollama:

```bash
ollama serve
```

Launch the application:

```bash
python main.py
```

---

# 🖥 GUI Features

The launcher automatically:

* Detects installed Ollama models
* Lists models in dropdown
* Loads selected model into memory
* Starts Telegram bot
* Initializes browser engine
* Enables headless or visible mode

---

# 📱 Usage

Open Telegram and send:

```text
Tata Salt
Ariel Liquid Top Load
Amul Taaza Milk
```

Example workflow:

```text
User Request
      ↓
Search All Platforms
      ↓
Extract Product Data
      ↓
LLM Evaluation
      ↓
Price Normalization
      ↓
Select Winner
      ↓
Add To Cart
      ↓
Generate Invoice
```

---

# 🧠 AI Evaluation Process

The local LLM receives:

```text
Product Name
Brand
Quantity
Price
Platform
Sponsored Status
```

The model then:

1. Verifies brand match
2. Rejects fake alternatives
3. Rejects sponsored bias
4. Computes normalized pricing
5. Selects best value product

Example:

```text
₹105 for 1kg
₹59 for 500g
```

Normalized:

```text
₹105/kg
₹118/kg
```

Winner:

```text
₹105/kg
```

---

# 🛠 Technology Stack

### Backend

* Python 3.10+
* Selenium
* Undetected ChromeDriver

### AI

* Ollama
* Gemma
* Llama
* Qwen
* Mistral

### Desktop UI

* CustomTkinter

### Messaging

* Telegram Bot API

### Reporting

* HTML/CSS Invoice Engine

---

# 📊 Example Output

```text
✓ Tata Salt
Platform: Blinkit
Price: ₹28

✓ Amul Taaza Milk
Platform: Zepto
Price: ₹56

✓ Ariel Liquid Top Load
Platform: BigBasket
Price: ₹185

Estimated Total:
₹269
```

---

# ⚠️ Disclaimer

This project is intended for:

* Educational use
* Research
* Personal automation

Users are responsible for complying with:

* Platform Terms of Service
* Applicable local laws
* Responsible rate limiting

The authors assume no liability for misuse of this software.

---

# 📄 License

MIT License

Feel free to modify, distribute, and improve the project under the terms of the MIT License.
