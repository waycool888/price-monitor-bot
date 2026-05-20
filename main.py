import os
import requests
from datetime import datetime

# -------------------------------------------------------------
# CORE CONFIGURATION
# -------------------------------------------------------------
BASE_CURRENCY = "SGD"
TARGET_CURRENCIES = ["MYR", "CNY"]

# Load Secure Vault Environment Variables
FOREX_KEY = os.environ.get("FOREX_API_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def broadcast_rates(rates_dict):
    """Formats and transmits the data stream payload directly to Telegram."""
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
    
    # Construct a clean, scannable notification interface
    message = f"🌏 *Current Forex Rates ({BASE_CURRENCY})*\n"
    message += f"🕒 _Updated: {timestamp}_\n\n"
    
    for currency, rate in rates_dict.items():
        message += f"• 1 {BASE_CURRENCY} = *{rate:.4f} {currency}*\n"
        
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Log: Rate data package dispatched to Telegram.")
    except Exception as e:
        print(f"Error executing Telegram push: {e}")

def pull_exchange_data():
    """Queries endpoint for spot market data fields."""
    print(f"Querying current market status for base asset: {BASE_CURRENCY}...")
    url = f"https://v6.exchangerate-api.com/v6/{FOREX_KEY}/latest/{BASE_CURRENCY}"
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data.get("result") == "success":
            all_rates = data.get("conversion_rates", {})
            
            # Filter and isolate only our requested target components
            filtered_rates = {
                curr: all_rates[curr] 
                for curr in TARGET_CURRENCIES 
                if curr in all_rates
            }
            
            print(f"Extracted Market Rates: {filtered_rates}")
            broadcast_rates(filtered_rates)
        else:
            print(f"API Error. Server Message: {data.get('error-type', 'Execution flag failure.')}")
            
    except Exception as e:
        print(f"Fatal data acquisition failure: {e}")

if __name__ == "__main__":
    pull_exchange_data()
            
