import os
import requests

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_message(text: str) -> None:
    if not TOKEN or not CHAT_ID:
        print("Telegram secrets missing. TELEGRAM_TOKEN / TELEGRAM_CHAT_ID not set.")
        print(text)
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}

    try:
        requests.post(url, data=payload, timeout=20)
    except Exception as e:
        print("Telegram send failed:", e)
