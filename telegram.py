import requests
from datetime import datetime

# 🔴 PASTE YOUR REAL TOKEN HERE
TELEGRAM_TOKEN = "8376092514:AAH9eCBiPYtjfupuN5CjziZZU9PoXNDzZh4"

# 🔴 YOUR CHAT ID (from getUpdates)
TELEGRAM_CHAT_ID = "6278230258"


def regime_emoji(regime):
    return {
        "BULLISH": "🟢",
        "BEARISH": "🔴",
        "NEUTRAL": "🟡"
    }.get(regime, "⚪")


def format_message(index, close, sma, regime, capital, stocks):

    emoji = regime_emoji(regime)
    date_str = datetime.now().strftime("%d %b %Y")

    message = f"""📊 BTST AI Engine – Trade Alert
🗓 {date_str}

Index: {index}
Close: {close}
SMA20: {sma}
Regime: {emoji} {regime}

💰 Total Capital: ₹{capital}
"""

    if not stocks:
        message += "\n\n⚠ No qualifying setups today."
        return message

    allocation = round(capital / len(stocks), 2)

    message += "\n\n🎯 Selected Stocks\n"

    for i, stock in enumerate(stocks, start=1):

        lower = round(stock["entry_price"] - (0.3 * stock["atr"]), 2)
        upper = round(stock["entry_price"] + (0.3 * stock["atr"]), 2)

        message += f"""
{i}. {stock['symbol']}
   💵 Allocation: ₹{allocation}
   📈 Current Price: ₹{stock['current_price']}
   📍 Entry Zone: {lower} – {upper}
   🎯 Confidence: {stock['final_score']}%
"""

    return message


def send_btst_alert(index, close, sma, regime, capital, stocks):

    message = format_message(index, close, sma, regime, capital, stocks)

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    response = requests.post(url, json=payload)

    def send_weekend_summary(close, sma, regime):

    from datetime import datetime

    emoji = {
        "BULLISH": "🟢",
        "BEARISH": "🔴",
        "NEUTRAL": "🟡"
    }.get(regime, "⚪")

    message = f"""📊 Weekend Market Recap

Last Friday Close: {close}
SMA20: {sma}
Regime: {emoji} {regime}

📌 Market closed for weekend.
BTST Engine will resume Monday morning.

— Powered by BTST AI Advisor
"""

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }

    response = requests.post(url, json=payload)

    print("Weekend Telegram Response:", response.text)

    return response.json()

    print("Telegram Response:", response.text)

    return response.json()
