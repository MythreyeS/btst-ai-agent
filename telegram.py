import requests
import os
from datetime import datetime


# ==============================
# 🔐 Secure Environment Variables
# ==============================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

MAX_MSG_LENGTH = 4000  # Telegram safety limit


# ==============================
# Utility Functions
# ==============================

def _emoji_regime(regime: str) -> str:
    return {
        "BULLISH": "🟢",
        "BEARISH": "🔴",
        "NEUTRAL": "🟡"
    }.get(regime, "⚪")


def _fmt_money(x):
    try:
        return f"₹{float(x):,.0f}"
    except Exception:
        return f"₹{x}"


def _send_message(text: str):
    """
    Sends message safely with auto-splitting
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Telegram credentials missing.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    # Split large messages safely
    parts = [text[i:i + MAX_MSG_LENGTH] for i in range(0, len(text), MAX_MSG_LENGTH)]

    for part in parts:
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": part
        }
        response = requests.post(url, json=payload)
        print("Telegram Response:", response.text)


# ==============================
# MAIN DAILY REPORT FUNCTION
# ==============================

def send_btst_daily_report(
    market_regime: dict,
    policy: dict,
    sector_top: dict,
    man_of_match: dict,
    movers: list
):

    date_str = datetime.now().strftime("%d %b %Y")
    regime = market_regime.get("regime", "NEUTRAL")
    emoji = _emoji_regime(regime)

    capital = float(policy.get("capital", 50000))
    risk_pct = float(policy.get("max_risk_pct_per_trade", 0.02))
    max_risk_rupees = capital * risk_pct

    msg = []

    # ==============================
    # HEADER
    # ==============================

    msg.append("📊 BTST AI Engine – Institutional Market Report")
    msg.append(f"🗓 Date: {date_str}")
    msg.append("")
    msg.append(f"Market Regime: {emoji} {regime}")
    msg.append(f"NIFTY Close: {market_regime.get('close')}")
    msg.append(f"SMA20: {market_regime.get('sma20')} | SMA50: {market_regime.get('sma50')}")
    msg.append("")

    msg.append(f"💰 Total Capital: {_fmt_money(capital)}")
    msg.append(f"⚠ Max Risk Per Trade: {_fmt_money(max_risk_rupees)} ({int(risk_pct*100)}%)")
    msg.append("🧠 Strategy: Buy at TODAY CLOSE ➜ Sell at TOMORROW OPEN.")
    msg.append("")

    # ==============================
    # MARKET BREADTH
    # ==============================

    if movers:
        total = len(movers)
        gainers = sum(1 for m in movers if float(m.get("intraday_pct", 0)) > 0)
        losers = total - gainers

        msg.append("📈 Market Breadth:")
        msg.append(f"Total Stocks Scanned: {total}")
        msg.append(f"Gainers: {gainers} | Losers: {losers}")
        msg.append("")

    # ==============================
    # SECTOR LEADER
    # ==============================

    if sector_top:
        msg.append("🏆 Strongest Sector Today:")
        msg.append(f"{sector_top.get('sector','Unknown')} "
                   f"(Avg Intraday: {sector_top.get('avg_intraday_pct')}%)")
        msg.append("")

    # ==============================
    # MAN OF THE MATCH
    # ==============================

    if man_of_match:
        msg.append("🔥 Man of the Match:")
        msg.append(f"{man_of_match.get('symbol')} "
                   f"| Sector: {man_of_match.get('sector','Unknown')}")
        msg.append(f"PrevClose {man_of_match.get('prev_close')} "
                   f"→ Open {man_of_match.get('day_open')} "
                   f"→ Close {man_of_match.get('day_close')}")
        msg.append(f"Gap {man_of_match.get('gap_pct')}% "
                   f"| Intraday {man_of_match.get('intraday_pct')}%")
        msg.append(f"Probability Edge: {man_of_match.get('probability_edge')}% "
                   f"| Conviction: {man_of_match.get('conviction')}")
        msg.append("")

    # ==============================
    # FULL TOP MOVERS
    # ==============================

    msg.append("📈 Full Top Movers – Ranked by Intraday Strength")
    msg.append("")

    if not movers:
        msg.append("⚠ No significant movers today.")
    else:
        sorted_movers = sorted(
            movers,
            key=lambda x: float(x.get("intraday_pct", 0)),
            reverse=True
        )

        for i, s in enumerate(sorted_movers, start=1):
            msg.append("")
            msg.append(f"{i}) {s.get('symbol')}  | {s.get('sector','Unknown')}")
            msg.append(f"PrevClose {s.get('prev_close')} "
                       f"→ Open {s.get('day_open')} "
                       f"→ Close {s.get('day_close')}")
            msg.append(f"Gap {s.get('gap_pct')}% "
                       f"| Intraday {s.get('intraday_pct')}%")
            msg.append(f"VolRatio {s.get('vol_ratio')} "
                       f"| CloseNearHigh {s.get('close_near_high')}")
            msg.append(f"ProbEdge {s.get('probability_edge')}% "
                       f"| Conviction {s.get('conviction')}")

    # ==============================
    # BEGINNER GUIDE
    # ==============================

    msg.append("")
    msg.append("📘 Beginner Guide:")
    msg.append("• Buy @ Close: Buy at today’s final price.")
    msg.append("• Tomorrow Open Exit: Sell at next session open.")
    msg.append("• Stop Loss: Exit level to control loss.")
    msg.append("• Probability Edge: Estimated chance of opening higher.")
    msg.append("• Conviction: Strength of signal.")
    msg.append("• Intraday %: Open to Close movement.")
    msg.append("")
   msg.append("⚠ AI-based system. Not guaranteed returns.")

# Finalize and send message
final_message = "\n".join(msg)
_send_message(final_message)


def send_telegram(message: str):
    """
    Backward-compatible wrapper.
    """
    return _send_message(message)
