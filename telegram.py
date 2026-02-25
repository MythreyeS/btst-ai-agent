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

    final_message = "\n".join(msg)

    _send_message(final_message)import requests
from datetime import datetime

TELEGRAM_TOKEN = "8376092514:AAH9eCBiPYtjfupuN5CjziZZU9PoXNDzZh4"
TELEGRAM_CHAT_ID = "6278230258"


def _emoji_regime(regime: str) -> str:
    return {"BULLISH": "🟢", "BEARISH": "🔴", "NEUTRAL": "🟡"}.get(regime, "⚪")


def _fmt_money(x):
    try:
        return f"₹{float(x):,.0f}"
    except Exception:
        return f"₹{x}"


def send_btst_daily_report(
    market_regime: dict,
    policy: dict,
    sector_top: dict,
    man_of_match: dict,
    top5: list
):
    date_str = datetime.now().strftime("%d %b %Y")
    regime = market_regime.get("regime", "NEUTRAL")
    emoji = _emoji_regime(regime)

    capital = float(policy.get("capital", 50000))
    risk_pct = float(policy.get("max_risk_pct_per_trade", 0.02))
    max_risk_rupees = capital * risk_pct

    msg = []
    msg.append(f"📊 BTST AI Engine – Close ➜ Next Open Strategy")
    msg.append(f"🗓 Date: {date_str}")
    msg.append("")
    msg.append(f"Index: {market_regime.get('index','NIFTY 50')}")
    msg.append(f"Market Regime: {emoji} {regime}")
    msg.append(f"Today NIFTY Close: {market_regime.get('close')}")
    msg.append(f"SMA20: {market_regime.get('sma20')} | SMA50: {market_regime.get('sma50')}")
    msg.append("")
    msg.append(f"💰 Total Capital: {_fmt_money(capital)}")
    msg.append(f"⚠ Max Risk Per Trade: {_fmt_money(max_risk_rupees)} ({int(risk_pct*100)}% of capital)")
    msg.append(f"🧠 Strategy: Buy at TODAY CLOSE and sell at TOMORROW OPEN.")
    msg.append("")

    # Sector summary
    if sector_top:
        msg.append("📌 Sector Strength Today:")
        msg.append(f"• Top Sector: {sector_top.get('sector','Unknown')} (Avg Intraday: {sector_top.get('avg_intraday_pct')}%)")
        msg.append("")

    # Man of the match
    if man_of_match:
        msg.append("🏆 Man of the Match (Best Setup Today):")
        msg.append(f"• Stock: {man_of_match['symbol']} | Sector: {man_of_match.get('sector','Unknown')}")
        msg.append(f"• Previous Close (yesterday end): {man_of_match['prev_close']}")
        msg.append(f"• Day Open (today start): {man_of_match['day_open']}")
        msg.append(f"• Day Close (today end / BTST buy price): {man_of_match['day_close']}")
        msg.append(f"• Gap Move (Prev Close→Open): {man_of_match['gap_pct']}%")
        msg.append(f"• Intraday Move (Open→Close): {man_of_match['intraday_pct']}%")
        msg.append(f"• Probability Edge (Close→Next Open Higher): {man_of_match['probability_edge']}%")
        msg.append(f"• Conviction: {man_of_match['conviction']}")
        msg.append("")

    # Top 5 picks
    msg.append("🎯 Top 5 BTST Recommendations (from NIFTY 500 scan):")

    if not top5:
        msg.append("⚠ No qualifying setups today based on filters.")
    else:
        for i, s in enumerate(top5, start=1):
            msg.append("")
            msg.append(f"{i}) {s['symbol']}  | Sector: {s.get('sector','Unknown')}")
            msg.append(f"📍 Buy @ Today Close: {s['day_close']}")
            msg.append(f"📤 Planned Exit: Tomorrow Open (next session opening)")
            msg.append(f"🛑 Stop Loss (safety exit): {s['stop']}")
            msg.append(f"🎯 Target (guidance): {s['target']}")
            msg.append(f"⚖ Risk:Reward (R:R): 1:{s['rr']}")
            msg.append(f"📊 Probability Edge: {s['probability_edge']}%  | Conviction: {s['conviction']}")
            msg.append(f"📦 Position Size (shares to buy): {s['position_qty']}")
            msg.append(f"💰 Capital Required: {_fmt_money(s['capital_required'])}")
            msg.append(f"⚠ Estimated Max Loss if SL hits: {_fmt_money(s['estimated_risk'])}")
            msg.append(f"📈 Today: PrevClose {s['prev_close']} → Open {s['day_open']} → Close {s['day_close']}")
            msg.append(f"🧾 Notes: VolRatio {s['vol_ratio']} | CloseNearHigh {s['close_near_high']} | Mom1D {s['mom_1d_pct']}%")

    # Beginner captions (daily)
    msg.append("")
    msg.append("📘 Beginner Guide (Simple Meaning):")
    msg.append("• Buy @ Close: Buy at today’s final market price.")
    msg.append("• Tomorrow Open Exit: Sell at next day market opening price.")
    msg.append("• Stop Loss: If price falls to this, exit to limit loss.")
    msg.append("• Target: Optional guidance level; markets may or may not reach it.")
    msg.append("• Position Size: Number of shares to buy so loss stays within max risk.")
    msg.append("• Probability Edge: Estimated chance of opening higher tomorrow (not a guarantee).")
    msg.append("• Conviction: Strength of signal (Low / Moderate / Strong).")
    msg.append("• R:R: If 1:2 means potential reward is ~2× the risk.")
    msg.append("")
    msg.append("⚠ Disclaimer: This is an AI-based signal system, not guaranteed returns. Use discipline.")

    final_message = "\n".join(msg)

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": final_message}
    resp = requests.post(url, json=payload)
    print("Telegram Response:", resp.text)
    return resp.json()
