import requests
from datetime import datetime

TELEGRAM_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"


# =====================================================
# UTILITIES
# =====================================================

def regime_emoji(regime):
    mapping = {
        "BULLISH": "🟢",
        "BEARISH": "🔴",
        "NEUTRAL": "🟡"
    }
    return mapping.get(regime.upper(), "⚪")


def profit_arrow(pnl_pct):
    if pnl_pct > 0:
        return "🟢▲"
    elif pnl_pct < 0:
        return "🔴▼"
    return "⚪➜"


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


def check_sl_target_hit(day_high, day_low, target, stop_loss):
    if day_high >= target:
        return "🎯 Target Hit"
    if day_low <= stop_loss:
        return "🛑 SL Hit"
    return "⏳ Running"


# =====================================================
# EVENING TRADE MESSAGE
# =====================================================

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
        sector = stock.get("sector", "Unknown")

        score = stock["final_score"]
        confidence = calculate_confidence(score)

        current_price = stock.get("current_price", 0)
        entry_price = stock.get("entry_price", current_price)
        atr = stock.get("atr", 10)
        volatility = stock.get("volatility", 0.02)

        stop_loss = stock.get("stop_loss", entry_price * 0.965)
        target = stock.get("target", entry_price * 1.05)

        lower, upper = calculate_entry_zone(entry_price, atr)
        risk = calculate_expected_risk(volatility)
        consensus = build_consensus_summary(stock)
        distance = calculate_distance_from_zone(current_price, lower, upper)

        message += f"""

{i}. *{symbol}* ({sector})
   💵 Allocation: ₹{allocation}
   📈 Current Price: ₹{current_price}
   📍 Entry Zone: {lower} – {upper}
   📊 Status: {distance}
   🎯 Confidence: {confidence}%
   ⚠ Expected Risk: {risk}%
   🤖 AI Consensus: {consensus}
   🛑 SL: ₹{round(stop_loss,2)}
   🎯 Target: ₹{round(target,2)}
"""

    message += "\n\n— Powered by BTST Agentic AI"
    return message


# =====================================================
# MORNING PERFORMANCE MESSAGE
# =====================================================

def format_morning_performance(trades):

    message = "📊 *Morning Performance Review*\n\n"

    message += "Stock | Buy | Now | P&L% | Signal | Status\n"
    message += "--------------------------------------------\n"

    for trade in trades:

        symbol = trade["symbol"]
        buy = trade["buy_price"]
        now = trade["current_price"]
        qty = trade["quantity"]

        stop = trade["stop_loss"]
        target = trade["target"]
        high = trade["day_high"]
        low = trade["day_low"]

        pnl_pct = ((now - buy) / buy) * 100
        arrow = profit_arrow(pnl_pct)
        status = check_sl_target_hit(high, low, target, stop)

        message += f"{symbol} | {buy} | {now} | {round(pnl_pct,2)}% {arrow} | {status}\n"

    message += "\n— Auto SL/Target Detection Enabled"
    return message


# =====================================================
# TELEGRAM SENDER
# =====================================================

def send_btst_alert(message):

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }

    response = requests.post(url, json=payload)
    return response.json()
