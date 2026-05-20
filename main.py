import os
import requests

# -------------------------------------------------------------
# CONFIGURATION TARGET VALUES (Modify these to suit your strategy)
# -------------------------------------------------------------
BASE_CURRENCY = "USD"       # Currency you are holding/comparing
TARGET_CURRENCY = "JPY"     # Currency you want to buy
TARGET_FX_RATE = 155.0      # ALERT TRIGGER: Ping me if 1 USD >= 155.0 JPY

# Load Secure Environment Variables
FOREX_KEY = os.environ.get("FOREX_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram_alert(message):
    """Dispatches a structured alert directly to your chat window."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID, 
        "text": message, 
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Log: Alert dispatched successfully.")
    except Exception as e:
        print(f"Error firing Telegram package: {e}")

def check_forex():
    """Queries public markets and evaluates structural margins."""
    print(f"Querying spot markets for {BASE_CURRENCY} variations...")
    url = f"https://v6.exchangerate-api.com/v6/{FOREX_KEY}/latest/{BASE_CURRENCY}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data.get("result") == "success":
            current_rate = data["conversion_rates"][TARGET_CURRENCY]
            print(f"Current Market Spot: 1 {BASE_CURRENCY} = {current_rate} {TARGET_CURRENCY}")
            
            # Target Trigger evaluation
            if current_rate >= TARGET_FX_RATE:
                alert_text = (
                    f"📈 *Forex Target Hit!*\n\n"
                    f"Exchange pairs have broken resistance criteria.\n"
                    f"*Pair:* {BASE_CURRENCY} to {TARGET_CURRENCY}\n"
                    f"*Current Rate:* `{current_rate}`\n"
                    f"*Target Threshold:* `{TARGET_FX_RATE}`"
                )
                send_telegram_alert(alert_text)
            else:
                print("Log: Market within expected boundaries. Threshold conditions unreached.")
        else:
            print(f"API Error. Server Responded: {data.get('error-type', 'Unknown error context')}")
            
    except Exception as e:
        print(f"Execution tracking anomaly: {e}")

if __name__ == "__main__":
    check_forex()
            
