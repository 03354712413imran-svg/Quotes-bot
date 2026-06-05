from flask import Flask, request, jsonify
import json
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

app = Flask(__name__)

# --- ستا د کوټیکس د ننوتلو معلومات ---
QUOTEX_EMAIL = "your_email@gmail.com"  # 👈 دلته خپل اصلي اېمیل ولیکه
QUOTEX_PASSWORD = "your_password123"   # 👈 دلته خپل اصلي پاسورډ ولیکه

trade_count = 0
MAX_TRADES = 6

def execute_quotex_trade(direction):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://qxbroker.com/en/sign-in")
            page.fill("input[name='email']", QUOTEX_EMAIL)
            page.fill("input[name='password']", QUOTEX_PASSWORD)
            page.click("button[type='submit']")
            time.sleep(5)
            
            if direction == "UP":
                page.click(".button-call") 
                print("🟢 په کوټیکس کې د UP بټن ووهل شوه!")
            elif direction == "DOWN":
                page.click(".button-put")
                print("🔴 په کوټیکس کې د DOWN بټن ووهل شوه!")
                
            browser.close()
    except Exception as e:
        print(f"❌ تېروتنه: {e}")

@app.route('/tradingview-webhook', methods=['POST'])
def webhook():
    global trade_count
    
    current_day = datetime.now().strftime('%A')
    if current_day in ['Saturday', 'Sunday']:
        print(f"⚠️ نن {current_day} (OTC مارکېټ) دی! سېګنال رد شو.")
        return jsonify({"status": "ignored", "reason": "OTC Market"}), 200

    if trade_count >= MAX_TRADES:
        return jsonify({"status": "ignored", "reason": "Daily limit reached"}), 200

    data = json.loads(request.data)
    direction = data.get("direction")
    
    trade_count += 1
    
    if trade_count in [1, 3, 5]:
        delay = 1
    else:
        delay = 2

    print(f"Live Market - Trade {trade_count}: د فېک کینډل د مخنیوي لپاره {delay} ثانیې صبر کوي...")
    time.sleep(delay)

    execute_quotex_trade(direction)
    return jsonify({"status": "success", "trade_number": trade_count, "delay_used": delay}), 200

if __name__ == '__main__':
    app.run(port=5000)
