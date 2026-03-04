import os
import requests

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
MAX_MESSAGE_LENGTH = 4000


def send_telegram(text: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials missing.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    # Split long messages safely
    parts = [text[i:i + MAX_MESSAGE_LENGTH] for i in range(0, len(text), MAX_MESSAGE_LENGTH)]

    for part in parts:
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": part,
            "parse_mode": "Markdown"
        }
        try:
            requests.post(url, json=payload, timeout=20)
        except Exception as e:
            print("Telegram send error:", e)


def _normalize_mover(m):
    """
    Accept dict OR string and normalize to dict.
    This prevents: string indices must be integers / 'str'.get errors
    """
    if isinstance(m, dict):
        return {
            "symbol": m.get("symbol", "N/A"),
            "sector": m.get("sector", "Unknown"),
            "change_pct": m.get("change_pct", 0),
            "prev_close": m.get("prev_close", 0),
            "close": m.get("close", 0),
        }

    if isinstance(m, str):
        return {
            "symbol": m,
            "sector": "Unknown",
            "change_pct": 0,
            "prev_close": 0,
            "close": 0,
        }

    return {
        "symbol": "N/A",
        "sector": "Unknown",
        "change_pct": 0,
        "prev_close": 0,
        "close": 0,
    }


def send_btst_daily_report(market_regime, policy, sector_top, man_of_match, movers):
    """
    Sends daily BTST report.
    This is robust even if movers contains strings accidentally.
    """

    movers = movers or []
    safe_movers = [_normalize_mover(m) for m in movers]

    mom = _normalize_mover(man_of_match) if man_of_match else {"symbol": "N/A", "sector": "Unknown"}

    msg = "📊 *BTST AI Advisor*\n\n"
    msg += f"🧭 Regime: *{market_regime}*\n"
    msg += f"🏁 Sector in Focus: *{sector_top}*\n\n"

    msg += "🏅 *Man of the Match*\n"
    msg += f"• {mom['symbol']} ({mom['sector']})\n\n"

    msg += "🔥 *Top 5 Movers*\n"
    if not safe_movers:
        msg += "• No movers found today.\n"
        send_telegram(msg)
        return

    for m in safe_movers[:5]:
        sym = m["symbol"]
        sec = m["sector"]
        chg = m["change_pct"]
        pc = m["prev_close"]
        cl = m["close"]

        # show prices only if available
        if pc and cl:
            msg += f"• *{sym}* ({sec}) | {chg}% | Prev: {pc} → Close: {cl}\n"
        else:
            msg += f"• *{sym}* ({sec})\n"

    send_telegram(msg)
