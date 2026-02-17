import yfinance as yf
from telegram import send_message
from capital_manager import load_capital, update_capital
from weekly_tracker import add_weekly_profit
from core.storage import append_csv, today_str
from trade_manager import load_trade, clear_trade

TRADES_CSV = "data/trades.csv"
FIELDS = ["date","symbol","entry","sl","target","qty","open","high","low","close","gap_pct","exit","outcome","pnl","capital_after","agent_score","risk_pct"]

def evaluate_open_trade():
    trade = load_trade()
    if not trade:
        send_message("ℹ️ No open BTST trade to evaluate today.")
        return

    symbol = trade["symbol"]
    entry = float(trade["entry"])
    sl = float(trade["sl"])
    target = float(trade["target"])
    qty = int(trade["qty"])
    agent_score = float(trade.get("agent_score", 0.0))
    risk_pct = float(trade.get("risk_pct", 0.0))

    df = yf.download(symbol + ".NS", period="5d", progress=False)
    if df is None or df.empty:
        send_message(f"⚠️ Cannot fetch prices for {symbol}.")
        return

    today = df.iloc[-1]
    o = float(today["Open"])
    h = float(today["High"])
    l = float(today["Low"])
    c = float(today["Close"])

    gap_pct = ((o - entry) / entry) * 100.0

    exit_price = c
    outcome = "CLOSE_EXIT"
    if h >= target:
        exit_price = target
        outcome = "TARGET_HIT"
    elif l <= sl:
        exit_price = sl
        outcome = "STOP_HIT"

    pnl = (exit_price - entry) * qty

    cap_before = load_capital()
    cap_after = cap_before + pnl
    update_capital(cap_after)

    weekly_pnl = add_weekly_profit(pnl)

    # log CSV
    append_csv(TRADES_CSV, {
        "date": today_str(),
        "symbol": symbol,
        "entry": entry,
        "sl": sl,
        "target": target,
        "qty": qty,
        "open": o,
        "high": h,
        "low": l,
        "close": c,
        "gap_pct": gap_pct,
        "exit": exit_price,
        "outcome": outcome,
        "pnl": pnl,
        "capital_after": cap_after,
        "agent_score": agent_score,
        "risk_pct": risk_pct
    }, FIELDS)

    gap_tag = "Gap Up ✅" if gap_pct > 0 else "Gap Down ⚠️" if gap_pct < 0 else "Flat"

    msg = (
        f"📊 BTST AI Result\n\n"
        f"{symbol}\n"
        f"Entry: ₹{entry:.2f}\n"
        f"Open: ₹{o:.2f} ({gap_tag} {gap_pct:.2f}%)\n"
        f"Exit: ₹{exit_price:.2f} ({outcome})\n"
        f"Qty: {qty}\n\n"
        f"P&L: ₹{pnl:,.0f}\n"
        f"Capital: ₹{cap_after:,.0f}\n"
        f"Weekly P&L: ₹{weekly_pnl:,.0f}\n"
    )

    send_message(msg)
    clear_trade()
