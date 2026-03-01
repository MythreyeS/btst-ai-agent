import os
import requests
from datetime import datetime

# ==========================================
# 🔐 Telegram Credentials (GitHub Secrets)
# ==========================================

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

MAX_MESSAGE_LENGTH = 4000


# ==========================================
# Internal Send Function (HTML Enabled)
# ==========================================

def _send_message(text: str):

    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials missing.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    parts = [
        text[i:i + MAX_MESSAGE_LENGTH]
        for i in range(0, len(text), MAX_MESSAGE_LENGTH)
    ]

    for part in parts:
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": part,
            "parse_mode": "HTML"
        }
        response = requests.post(url, json=payload)
        print("Telegram Response:", response.text)


# ==========================================
# MAIN BTST DAILY REPORT
# ==========================================

def send_btst_daily_report(
    market_regime: dict,
    policy: dict,
    sector_top: dict,
    man_of_match: dict,
    movers: list
):

    date_str = datetime.now().strftime("%d %b %Y")
    msg = []

    # ======================================
    # HEADER
    # ======================================

    msg.append("📊 <b>BTST AI Engine – Institutional Market Report</b>")
    msg.append(f"🗓 <b>Date:</b> {date_str}")
    msg.append("")

    # ======================================
    # MARKET REGIME
    # ======================================

    if market_regime:
        msg.append(f"<b>Market Regime:</b> {market_regime.get('regime')}")
        msg.append(f"NIFTY Close: {market_regime.get('close')}")
        msg.append(
            f"SMA20: {market_regime.get('sma20')} | "
            f"SMA50: {market_regime.get('sma50')}"
        )
        msg.append("")

    # ======================================
    # CAPITAL POLICY
    # ======================================

    if policy:
        msg.append(f"💰 <b>Capital:</b> ₹{policy.get('capital')}")
        msg.append(
            f"⚠ <b>Max Risk Per Trade:</b> "
            f"{policy.get('max_risk_pct_per_trade')}"
        )
        msg.append("")

    # ======================================
    # STRONGEST SECTOR
    # ======================================

    if sector_top:
        msg.append("🏆 <b>Strongest Sector Today</b>")
        msg.append(
            f"{sector_top.get('sector')} "
            f"(Avg Intraday: {sector_top.get('avg_intraday_pct')}%)"
        )
        msg.append("")

    # ======================================
    # MAN OF THE MATCH (Intraday)
    # ======================================

    if man_of_match:
        msg.append("🔥 <b>Man of the Match</b>")
        msg.append(
            f"{man_of_match.get('symbol')} | "
            f"{man_of_match.get('sector')}"
        )
        msg.append(
            f"PrevClose {man_of_match.get('prev_close')} → "
            f"Open {man_of_match.get('day_open')} → "
            f"High {man_of_match.get('day_high')} → "
            f"Close {man_of_match.get('day_close')}"
        )
        msg.append("")

    # ======================================
    # YESTERDAY SUGGESTED STOCKS – PERFORMANCE
    # ======================================

    msg.append("📊 <b>Yesterday Suggested Stocks – Performance Review</b>")
    msg.append("<pre>")

    header = f"{'Symbol':<10}{'Sector':<15}{'Buy':>8}{'Now':>8}{'P/L%':>8}   Status"
    msg.append(header)
    msg.append("-" * 70)

    sector_summary = {}
    best_stock = None
    best_return = -999

    if movers:

        for s in movers:

            symbol = s.get("symbol", "")[:9]
            sector = s.get("sector", "Unknown")[:14]

            buy_price = float(s.get("prev_close", 0))
            now_price = float(s.get("day_close", 0))
            high = float(s.get("day_high", 0))
            low = float(s.get("day_low", 0))

            stop_loss = s.get("stop_loss")
            target = s.get("target")

            pnl_pct = (
                ((now_price - buy_price) / buy_price) * 100
                if buy_price else 0
            )

            # Arrow indicator
            if pnl_pct > 0:
                arrow = "🟢▲"
            elif pnl_pct < 0:
                arrow = "🔴▼"
            else:
                arrow = "⚪"

            # SL / Target detection
            status = "Running"
            if target and high >= target:
                status = "🎯 Target Hit"
            elif stop_loss and low <= stop_loss:
                status = "🛑 SL Hit"

            row = (
                f"{symbol:<10}"
                f"{sector:<15}"
                f"{buy_price:>8.2f}"
                f"{now_price:>8.2f}"
                f"{pnl_pct:>7.2f}% {arrow}  "
                f"{status}"
            )

            msg.append(row)

            # Track best performer
            if pnl_pct > best_return:
                best_return = pnl_pct
                best_stock = symbol

            # Sector aggregation
            if sector not in sector_summary:
                sector_summary[sector] = []

            sector_summary[sector].append(pnl_pct)

    else:
        msg.append("No suggested stocks.")

    msg.append("</pre>")
    msg.append("")

    # ======================================
    # BEST PERFORMER (Portfolio)
    # ======================================

    if best_stock:
        msg.append(
            f"🏆 <b>Best Performer:</b> "
            f"{best_stock} ({round(best_return,2)}%)"
        )
        msg.append("")

    # ======================================
    # FULL SECTOR SUMMARY
    # ======================================

    if sector_summary:
        msg.append("📈 <b>Sector Performance Summary</b>")

        for sector, returns in sector_summary.items():
            avg_return = sum(returns) / len(returns)

            if avg_return > 0:
                sector_arrow = "🟢▲"
            elif avg_return < 0:
                sector_arrow = "🔴▼"
            else:
                sector_arrow = "⚪"

            msg.append(
                f"{sector}: {round(avg_return,2)}% {sector_arrow}"
            )

        msg.append("")

    # ======================================
    # TOP 10 MOVERS
    # ======================================

    msg.append("📈 <b>Top Movers Today</b>")

    if movers:
        sorted_movers = sorted(
            movers,
            key=lambda x: float(x.get("intraday_pct", 0)),
            reverse=True
        )

        for i, s in enumerate(sorted_movers[:10], start=1):
            msg.append(
                f"{i}) {s.get('symbol')} | "
                f"{s.get('intraday_pct')}% | "
                f"Prob: {s.get('probability_edge')}%"
            )
    else:
        msg.append("No significant movers.")

    msg.append("")
    msg.append("⚠ AI-based system. Not guaranteed returns.")

    final_message = "\n".join(msg)
    _send_message(final_message)


# ==========================================
# Simple Wrapper
# ==========================================

def send_telegram(message: str):
    _send_message(message)
