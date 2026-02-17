import os
import requests

def send_message(text: str) -> bool:
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("Telegram env vars missing: TELEGRAM_TOKEN / TELEGRAM_CHAT_ID")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}

    try:
        r = requests.post(url, data=payload, timeout=30)
        if r.status_code != 200:
            print("Telegram error:", r.text)
            return False
        return True
    except Exception as e:
        print("Telegram exception:", e)
        return False
