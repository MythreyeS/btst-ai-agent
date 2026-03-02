import sys
import json
import yfinance as yf

from agents.regime_agent import get_market_regime
from btst_orchestrator import run_btst_agents
from core.universe_manager import load_universe, get_sector
from telegram import send_telegram

CAPITAL = 100000


def _arrow(pct: float) -> str:
    # Telegram doesn't support colors; we simulate with emojis
    if pct > 0.05:
        return "🟢▲"
    if pct < -0.05:
        return "🔴▼"
    return "⚪➜"


def _hit_status(day_high: float, day_low: float, target: float, stop: float) -> str:
    hit_t = day_high >= target
    hit_s = day_low <= stop

    if hit_t and hit_s:
        return "⚠️ Both Hit"
    if hit_t:
        return "🎯 Target Hit"
    if hit_s:
        return "🛑 SL Hit"
    return "⏳ Running"


def evening_btst():
    regime, close, sma20 = get_market_regime()
    universe = load_universe()

    header = f"""<b>📊 BTST AI Advisor</b>

📈 <b>Nifty Close:</b> {close:.2f}
📉 <b>SMA20:</b> {sma20:.2f}
🧭 <b>Regime:</b> {regime}
"""

    if regime == "BEARISH":
    regime_note = "⚠ Bearish – Hunter Mode Active"
else:
    regime_note = "🚀 Bullish Momentum"

# Continue scanning stocks normally
    selected = run_btst_agents(universe)

    if not selected:
        msg = header + "\n\n⚠️ No valid BTST setups found today."
        send_telegram(msg)
        return

    capital_per_stock = CAPITAL / len(selected)
    trade_data = []

    msg = header + "\n\n<b>✅ BTST Picks (Buy at Close)</b>\n"

    for sym in selected:
        data = yf.download(sym, period="2d", interval="1d", progress=False)
        if data.empty or len(data) < 2:
            continue

        prev_close = float(data["Close"].iloc[-2])
        today_open = float(data["Open"].iloc[-1])
        today_close = float(data["Close"].iloc[-1])

        buy = today_close
        qty = int(capital_per_stock / buy) if buy > 0 else 0

        # Your style (can tune later)
        stop = buy * 0.965
        target = buy * 1.05
        rr = (target - buy) / (buy - stop) if (buy - stop) != 0 else 0

        capital_req = qty * buy
        max_loss = qty * (buy - stop)

        trade_data.append({
            "symbol": sym,
            "sector": get_sector(sym),
            "buy_price": buy,
            "quantity": qty,
            "stop_loss": stop,
            "target": target,
            "prev_close": prev_close,
            "today_open": today_open,
            "today_close": today_close
        })

        msg += f"""
━━━━━━━━━━━━━━━━━━
<b>📌 {sym.split('.')[0]}</b>   <i>({get_sector(sym)})</i>
━━━━━━━━━━━━━━━━━━

🛒 <b>Buy:</b> ₹{buy:.2f}
🚪 <b>Exit:</b> Tomorrow Open
🛑 <b>Stop:</b> ₹{stop:.2f}
🎯 <b>Target:</b> ₹{target:.2f}
⚖ <b>R:R:</b> 1:{rr:.2f}

📦 <b>Qty:</b> {qty}
💰 <b>Capital:</b> ₹{int(capital_req)}
⚠ <b>Max Loss:</b> ₹{int(max_loss)}

📅 <b>Today:</b> Prev {prev_close:.2f} → Open {today_open:.2f} → Close {today_close:.2f}
"""

    # Save trades for morning review
    with open("btst_trades.json", "w") as f:
        json.dump(trade_data, f)

    beginner = """
━━━━━━━━━━━━━━━━━━
<b>📘 Beginner Guide (Simple Meaning)</b>

🔹 <b>Buy @ Close</b>: Buy at today’s final price
🔹 <b>Tomorrow Open Exit</b>: Sell at next day opening
🔹 <b>Stop Loss</b>: Exit level to protect capital
🔹 <b>Target</b>: Guidance level (not guaranteed)
🔹 <b>Qty</b>: Shares to buy
🔹 <b>R:R</b>: Risk:Reward (1:2 means reward ≈ 2× risk)

<i>Note: Signals are probabilistic. Risk management is mandatory.</i>
"""
    send_telegram(msg + beginner)


def morning_update():
    try:
        with open("btst_trades.json", "r") as f:
            trades = json.load(f)
    except Exception:
        send_telegram("⚠️ No previous BTST trades found to review.")
        return

    # ---------- PERFORMANCE TABLE ----------
    total_invested = 0.0
    total_pnl = 0.0

    lines = []
    for t in trades:
        sym = t["symbol"]
        buy = float(t["buy_price"])
        qty = int(t["quantity"])
        stop = float(t["stop_loss"])
        target = float(t["target"])

        # We use today's OHLC (latest candle)
        d = yf.download(sym, period="1d", interval="1d", progress=False)
        if d.empty:
            continue

        today_open = float(d["Open"].iloc[-1])
        today_high = float(d["High"].iloc[-1])
        today_low = float(d["Low"].iloc[-1])
        today_close = float(d["Close"].iloc[-1])

        # Status (SL/Target hit)
        status = _hit_status(today_high, today_low, target, stop)

        invested = buy * qty
        pnl = (today_close - buy) * qty
        pct = ((today_close - buy) / buy) * 100 if buy else 0.0
        total_invested += invested
        total_pnl += pnl

        arrow = _arrow(pct)
        sector = t.get("sector", get_sector(sym))
        name = sym.split(".")[0]

        # Keep columns tight for Telegram <pre>
        lines.append(
            f"{name:<10} {sector:<10} {buy:>7.2f} {today_close:>7.2f} {qty:>4} {pct:>6.2f}% {arrow} {status}"
        )

    net_pct = (total_pnl / total_invested) * 100 if total_invested else 0.0
    net_arrow = _arrow(net_pct)

    msg = "<b>📊 Morning Status + Performance</b>\n\n"
    msg += "<b>✅ Yesterday BTST P&L (Auto SL/Target detection)</b>\n"
    msg += "<pre>"
    msg += "Stock      Sector     Buy     Now    Qty   P&L %  Sig  Status\n"
    msg += "-----------------------------------------------------------------------\n"
    msg += "\n".join(lines) if lines else "No rows (data missing)\n"
    msg += "\n</pre>"

    msg += f"\n💰 <b>Total Invested:</b> ₹{int(total_invested)}"
    msg += f"\n📈 <b>Net P&L:</b> ₹{int(total_pnl)}"
    msg += f"\n📊 <b>Net Return:</b> {net_pct:.2f}% {net_arrow}\n"

    # ---------- TOP 10 INFUSION + SECTOR SUMMARY ----------
    universe = load_universe()
    candidates = []

    for sym in universe:
        try:
            d = yf.download(sym, period="2d", interval="1d", progress=False)
            if len(d) < 2:
                continue
            prev_close = float(d["Close"].iloc[-2])
            open_today = float(d["Open"].iloc[-1])
            gap_pct = ((open_today - prev_close) / prev_close) * 100 if prev_close else 0.0
            if gap_pct > 0.4:
                candidates.append((sym, gap_pct))
        except Exception:
            continue

    candidates = sorted(candidates, key=lambda x: x[1], reverse=True)[:10]

    msg += "\n<b>🚀 Top 10 Stocks to Infuse Today (Gap Leaders)</b>\n"
    msg += "<pre>"
    msg += "Rank  Stock       Sector       Gap%\n"
    msg += "----------------------------------------\n"
    for i, (sym, gap) in enumerate(candidates, start=1):
        name = sym.split(".")[0]
        sector = get_sector(sym)
        msg += f"{i:<4}  {name:<10} {sector:<12} {gap:>6.2f}%\n"
    msg += "</pre>"

    # Sector summary from candidates
    sector_bucket = {}
    for sym, gap in candidates:
        sec = get_sector(sym)
        if sec not in sector_bucket:
            sector_bucket[sec] = {"count": 0, "best": gap, "top": sym}
        sector_bucket[sec]["count"] += 1
        if gap > sector_bucket[sec]["best"]:
            sector_bucket[sec]["best"] = gap
            sector_bucket[sec]["top"] = sym

    if sector_bucket:
        msg += "\n<b>🧩 Sector Summary (from Top 10)</b>\n"
        msg += "<pre>"
        msg += "Sector        Cnt  BestGap  TopStock\n"
        msg += "----------------------------------------\n"
        # sort sectors by count desc then best gap desc
        for sec, info in sorted(sector_bucket.items(), key=lambda kv: (kv[1]["count"], kv[1]["best"]), reverse=True):
            top_name = info["top"].split(".")[0]
            msg += f"{sec:<12} {info['count']:<3} {info['best']:>7.2f}%  {top_name}\n"
        msg += "</pre>"

    send_telegram(msg)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "evening"
    if mode == "morning":
        morning_update()
    else:
        evening_btst()


if __name__ == "__main__":
    main()
