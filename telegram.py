import os
import requests


def send_message(message: str):
    """
    Sends a message to Telegram using bot token and chat ID
    stored in GitHub Secrets.
    """

    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("Telegram token or chat ID not configured.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": message
    }

    try:
        response = requests.post(url, data=payload)
        print("Telegram response:", response.text)
    except Exception as e:
        print("Telegram send failed:", str(e))
