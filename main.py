import os
import requests

# Load Secrets from Vault
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_test_message():
    """Dispatches a direct connectivity verification ping."""
    print("Initializing connection verification protocol...")
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID, 
        "text": "🚀 *System Connection Confirmed!*\nYour GitHub Actions automated container is talking to your Telegram handset successfully.",
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print("Success: Notification packet pushed to endpoint.")
    except Exception as e:
        print(f"Network Failure: {e}")
        # Print a diagnostic reminder if variables are unassigned
        if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
            print("CRITICAL: Check your GitHub Actions Secrets configuration fields.")

if __name__ == "__main__":
    send_test_message()
    
