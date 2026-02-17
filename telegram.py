import os
import requests
import json
from datetime import datetime

# ==============================
# TELEGRAM CONFIGURATION
# ==============================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# ==============================
# CORE SEND FUNCTION
# ==============================

def send_telegram_message(message: str):
    """
    Sends plain text message to Telegram.
    """

    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Telegram token or chat ID not configured.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, data=payload)
        result = response.json()
        print("Telegram Response:", result)
    except Exception as e:
        print("Telegram Error:", str(e))


# ==============================
# FORMATTED BTST SIGNAL PUSH
# ==============================

def send_btst_signal(symbol, entry, sl, target, quantity, confidence=None):
    """
    Sends formatted BTST trade signal.
    """

    now = datetime.now().strftime("%d-%b-%Y %H:%M")

    message = f"""
🚀 *BTST AI SIGNAL*

📊 Stock: *{symbol}*
💰 Entry: `{entry}`
🛑 Stop Loss: `{sl}`
🎯 Target: `{target}`
📦 Quantity: `{quantity}`

"""

    if confidence:
        message += f"🤖 Confidence Score: *{confidence}%*\n"

    message += f"\n⏰ Generated at: {now}\n"
    message += "\n⚠️ Risk Managed | AI Powered Strategy"

    send_telegram_message(message)


# ==============================
# WEEKLY PERFORMANCE MESSAGE
# ==============================

def send_weekly_report(total_pnl, win_rate, trades_taken):
    """
    Sends weekly performance summary.
    """

    message = f"""
📈 *WEEKLY PERFORMANCE REPORT*

💵 Total P&L: ₹{total_pnl}
🎯 Win Rate: {win_rate}%
🔁 Trades Taken: {trades_taken}

🔥 Goal: ₹20,000/week
"""

    send_telegram_message(message)


# ==============================
# SIMPLE TEST FUNCTION
# ==============================

if __name__ == "__main__":
    send_telegram_message("🔥 BTST AI Agent is LIVE and Connected!")

