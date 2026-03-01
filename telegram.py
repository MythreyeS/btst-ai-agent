import os
import requests
from datetime import datetime

# ==========================================
# 🔐 Telegram Credentials (GitHub Secrets)
# ==========================================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

MAX_MESSAGE_LENGTH = 4000  # Telegram limit safety


# ==========================================
# Internal Send Function
# ==========================================

def _send_message(text: str):
    """
    Sends message to Telegram with auto-splitting.
    """
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials missing.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    # Split if too long
    parts = [
        text[i:i + MAX_MESSAGE_LENGTH]
        for i in range(0, len(text), MAX_MESSAGE_LENGTH)
    ]

    for part in parts:
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": part
        }
        response = requests.post(url, json=payload)
        print("Telegram Response:", response.text)


# ==========================================
# Main BTST Daily Report Sender
# ==========================================

def send_btst_daily_report(
    market_regime: dict,
    policy: dict,
    sector_top: dict,
    man_of_match: dict,
    movers: list
):
    """
    Builds and sends the full BTST daily Telegram report.
    """

    date_str = datetime.now().strftime("%d %b %Y")

    msg = []

    # =============================
    # Header
    # =============================
    msg.append("📊 BTST AI Engine – Institutional Market Report")
    msg.append(f"🗓 Date: {date_str}")
    msg.append("")

    # =============================
    # Market Regime
    # =============================
    if market_regime:
        msg.append(f"Market Regime: {market_regime.get('regime')}")
        msg.append(f"NIFTY Close: {market_regime.get('close')}")
        msg.append(
            f"SMA20: {market_regime.get('sma20')} | "
            f"SMA50: {market_regime.get('sma50')}"
        )
        msg.append("")

    # =============================
    # Capital Policy
    # =============================
    if policy:
        capital = policy.get("capital")
        risk_pct = policy.get("max_risk_pct_per_trade")
        msg.append(f"💰 Capital: {capital}")
        msg.append(f"⚠ Max Risk Per Trade: {risk_pct}")
        msg.append("")

    # =============================
    # Strongest Sector
    # =============================
    if sector_top:
        msg.append("🏆 Strongest Sector Today:")
        msg.append(
            f"{sector_top.get('sector')} "
            f"(Avg Intraday: {sector_top.get('avg_intraday_pct')}%)"
        )
        msg.append("")

    # =============================
    # Man of the Match
    # =============================
    if man_of_match:
        msg.append("🔥 Man of the Match:")
        msg.append(
            f"{man_of_match.get('symbol')} | "
            f"{man_of_match.get('sector')}"
        )
        msg.append(
            f"PrevClose {man_of_match.get('prev_close')} → "
            f"Open {man_of_match.get('day_open')} → "
            f"Close {man_of_match.get('day_close')}"
        )
        msg.append("")

    # =============================
    # Full Movers List
    # =============================
    msg.append("📈 Top Movers Today:")

    if movers:
        sorted_movers = sorted(
            movers,
            key=lambda x: float(x.get("intraday_pct", 0)),
            reverse=True
        )

        for i, s in enumerate(sorted_movers, start=1):
            msg.append(
                f"{i}) {s.get('symbol')} | "
                f"Intraday: {s.get('intraday_pct')}% | "
                f"Prob: {s.get('probability_edge')}%"
            )
    else:
        msg.append("No significant movers.")

    msg.append("")
    msg.append("⚠ AI-based system. Not guaranteed returns.")

    # =============================
    # Final Send
    # =============================

    final_message = "\n".join(msg)
    _send_message(final_message)


# ==========================================
# Backward-Compatible Wrapper
# ==========================================

def send_telegram(message: str):
    """
    Simple wrapper for basic text sending.
    """
    _send_message(message)
