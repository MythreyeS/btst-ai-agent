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
    # Convert score out of 100 to %
    return round(score, 1)

def calculate_expected_risk(volatility):
    # Convert volatility to percentage
    return round(volatility * 100, 2)

def calculate_entry_zone(entry_price, atr):
    lower = round(entry_price - (0.3 * atr), 2)
    upper = round(entry_price + (0.3 * atr), 2)
    return f"{lower} – {upper}"

def build_consensus_summary(stock):
    votes = stock.get("votes", {})
    total_signals = len(votes)
    positive_signals = sum(votes.values())
    return f"{positive_signals}/{total_signals} AI signals aligned"

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
        message += "\n⚠ No qualifying setups today.\n"
        return message

    allocation_per_stock = round(capital / len(selected_stocks), 2)

    message += "\n🎯 *Selected Stocks*\n"

    for i, stock in enumerate(selected_stocks, start=1):

        symbol = stock['symbol']
        score = stock['final_score']
        confidence = calculate_confidence(score)
        risk = calculate_expected_risk(stock.get('volatility', 0.02))
        entry_zone = calculate_entry_zone(
            stock.get('entry_price', 0),
            stock.get('atr', 10)
        )
        consensus = build_consensus_summary(stock)

        message += f"""
{i}. *{symbol}*
   💵 Allocation: ₹{allocation_per_stock}
   🎯 Confidence: {confidence}%
   ⚠ Expected Risk: {risk}%
   📍 Entry Zone: {entry_zone}
   🤖 AI Consensus: {consensus}
"""

    message += "\n— Powered by BTST Agentic AI"

    return message


def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    response = requests.post(url, json=payload)
    return response.json()


def send_btst_alert(index, close, sma, regime, capital, selected_stocks):

    message = format_trade_message(
        index=index,
        close=close,
        sma=sma,
        regime=regime,
        capital=capital,
        selected_stocks=selected_stocks
    )

    return send_telegram_message(message)
