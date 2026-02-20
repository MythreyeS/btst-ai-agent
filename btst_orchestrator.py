import requests
from datetime import datetime

TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"


def regime_emoji(regime):
    mapping = {
        "BULLISH": "🟢",
        "BEARISH": "🔴",
        "NEUTRAL": "🟡"
    }
    return mapping.get(regime.upper(), "⚪")


def calculate_confidence(score):
    return round(score, 1)


def calculate_expected_risk(volatility):
    return round(volatility * 100, 2)


def calculate_entry_zone(entry_price, atr):
    lower = round(entry_price - (0.3 * atr), 2)
    upper = round(entry_price + (0.3 * atr), 2)
    return lower, upper


def calculate_distance_from_zone(current_price, lower, upper):
    if lower <= current_price <= upper:
        return "Inside Entry Zone ✅"
    elif current_price > upper:
        diff = ((current_price - upper) / upper) * 100
        return f"+{round(diff,2)}% Above Zone ⚠"
    else:
        diff = ((lower - current_price) / lower) * 100
        return f"-{round(diff,2)}% Below Zone ⚠"


def build_consensus_summary(stock):
    votes = stock.get("votes", {})
    total = len(votes)
    aligned = sum(votes.values())
    return f"{aligned}/{total} AI signals aligned"


def format_trade_message(index, close, sma, regime, capital, selected_stocks):

    emoji = regime_emoji(regime)
    date_str = datetime.now().strftime("%d %b %Y")

    message = f"""📊 *BTST AI Engine – Trade Alert*
🗓 {date_str}

Index: {index}
Close: {close}
SMA20: {sma}
Regime: {emoji} {regime}

💰 Total Capital: ₹{capital}
"""

    if not selected_stocks:
        message += "\n⚠ No qualifying setups today."
        return message

    allocation = round(capital / len(selected_stocks), 2)

    message += "\n\n🎯 *Selected Stocks*"

    for i, stock in enumerate(selected_stocks, start=1):

        symbol = stock["symbol"]
        score = stock["final_score"]
        confidence = calculate_confidence(score)

        current_price = stock.get("current_price", 0)
        entry_price = stock.get("entry_price", current_price)
        atr = stock.get("atr", 10)
        volatility = stock.get("volatility", 0.02)

        lower, upper = calculate_entry_zone(entry_price, atr)
        risk = calculate_expected_risk(volatility)
        consensus = build_consensus_summary(stock)
        distance = calculate_distance_from_zone(current_price, lower, upper)

        message += f"""

{i}. *{symbol}*
   💵 Allocation: ₹{allocation}
   📈 Current Price: ₹{current_price}
   📍 Entry Zone: {lower} – {upper}
   📊 Status: {distance}
   🎯 Confidence: {confidence}%
   ⚠ Expected Risk: {risk}%
   🤖 AI Consensus: {consensus}
"""

    message += "\n\n— Powered by BTST Agentic AI"

    return message


def send_btst_alert(index, close, sma, regime, capital, selected_stocks):

    message = format_trade_message(
        index, close, sma, regime, capital, selected_stocks
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    response = requests.post(url, json=payload)
    return response.json()
