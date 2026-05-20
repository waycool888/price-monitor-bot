import os
import requests

# -------------------------------------------------------------
# 1. CONFIGURATION & TARGET VALUES (Adjust these to your preference)
# -------------------------------------------------------------
# Currency monitoring
BASE_CURRENCY = "USD"
TARGET_CURRENCY = "EUR"
MAX_FOREX_RATE = 0.95  # Alert me if 1 USD buys MORE than 0.95 EUR

# Flight monitoring (Uses IATA Airport Codes. Example: SIN = Singapore, NRT = Tokyo)
FLIGHT_ORIGIN = "SIN"
FLIGHT_DESTINATION = "NRT"
MAX_FLIGHT_PRICE = 450  # Alert me if the cheapest ticket drops below $450 USD

# -------------------------------------------------------------
# 2. LOAD SECRETS FROM VAULT
# -------------------------------------------------------------
FOREX_KEY = os.environ.get("FOREX_API_KEY")
RAPIDAPI_KEY = os.environ.get("RAPIDAPI_KEY")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram_alert(message):
    """Dispatches a direct ping to your Telegram account."""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"Telegram error: {e}")

def check_forex():
    """Queries exchange rates and evaluates against threshold target."""
    url = f"https://v6.exchangerate-api.com/v6/{FOREX_KEY}/latest/{BASE_CURRENCY}"
    try:
        res = requests.get(url).json()
        if res.get("result") == "success":
            current_rate = res["conversion_rates"][TARGET_CURRENCY]
            print(f"Current Forex [{BASE_CURRENCY} to {TARGET_CURRENCY}]: {current_rate}")
            
            if current_rate >= MAX_FOREX_RATE:
                send_telegram_alert(f"📈 *Forex Alert!* 1 {BASE_CURRENCY} is now worth *{current_rate} {TARGET_CURRENCY}* (Target: {MAX_FOREX_RATE})")
        else:
            print("Forex API error structural breakdown flag.")
    except Exception as e:
        print(f"Forex data pull failure: {e}")

def check_flights():
    """Queries Travelpayouts cache for cheapest available rates."""
    url = "https://travelpayouts-travelpayouts-flight-data-v1.p.rapidapi.com/v1/prices/cheap"
    querystring = {
        "origin": FLIGHT_ORIGIN,
        "destination": FLIGHT_DESTINATION,
        "currency": "usd"
    }
    headers = {
        "x-access-token": RAPIDAPI_KEY, # RapidAPI passes this proxy through to Travelpayouts
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "travelpayouts-travelpayouts-flight-data-v1.p.rapidapi.com"
    }
    try:
        res = requests.get(url, headers=headers, params=querystring).json()
        if res.get("success") and FLIGHT_DESTINATION in res.get("data", {}):
            # Parse the inner nested dictionary data returned by the system cached payload
            flight_options = res["data"][FLIGHT_DESTINATION]
            # Find the lowest numerical cost from cached iterations
            cheapest_price = min([details["price"] for details in flight_options.values()])
            print(f"Cheapest Flight [{FLIGHT_ORIGIN} to {FLIGHT_DESTINATION}]: ${cheapest_price}")
            
            if cheapest_price <= MAX_FLIGHT_PRICE:
                send_telegram_alert(f"✈️ *Flight Price Drop!* Lowest route from {FLIGHT_ORIGIN} to {FLIGHT_DESTINATION} is down to *${cheapest_price} USD* (Target: ${MAX_FLIGHT_PRICE})")
        else:
            print("No matching cached flight data segments found.")
    except Exception as e:
        print(f"Flight system execution error: {e}")

if __name__ == "__main__":
    # Execute checks sequentially
    check_forex()
    check_flights()
  
