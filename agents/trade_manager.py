import os
import pandas as pd
import yfinance as yf
from datetime import datetime
from core.utils import load_json, save_json, ensure_dir
from capital_manager import get_capital, set_capital

OPEN_TRADE_PATH = "data/open_trade.json"
TRADES_CSV_PATH = "data/trades.csv"

def _init_trades_csv():
    ensure_dir("data")
    if not os.path.exists(TRADES_CSV_PATH):
        pd.DataFrame(columns=[
            "entry_date","exit_date","symbol","entry","exit","qty","pnl","pnl_pct","exit_reason"
        ]).to_csv(TRADES_CSV_PATH, index=False)

def save_open_trade(trade: dict) -> None:
    save_json(OPEN_TRADE_PATH, trade)

def load_open_trade() -> dict:
    return load_json(OPEN_TRADE_PATH, {})

def clear_open_trade() -> None:
    save_json(OPEN_TRADE_PATH, {})

def has_open_trade() -> bool:
    t = load_open_trade()
    return bool(t and t.get("symbol"))

def close_trade_if_due() -> dict:
    """
    If there is an open trade, fetch next trading day OHLC and close it:
    - if Low <= SL -> SL
    - elif High >= Target -> Target
    - else -> Close
    """
    _init_trades_csv()
    t = load_open_trade()
    if not t or not t.get("symbol"):
        return {"status": "no_open_trade"}

    symbol = t["symbol"]
    entry_date = t["entry_date"]
    entry = float(t["entry"])
    sl = float(t["stop_loss"])
    target = float(t["target"])
    qty = int(t["quantity"])

    # Get last 7 days to include next trading session
    df = yf.download(symbol, period="10d", interval="1d", progress=False)
    if df is None or df.empty:
        return {"status": "data_unavailable", "symbol": symbol}

    df = df.dropna()
    if df.empty:
        return {"status": "data_unavailable", "symbol": symbol}

    # Find entry index by date (best effort)
    df_idx = [x.date().isoformat() for x in df.index]
    if entry_date not in df_idx:
        # If not found, just use last two rows for closure
        if len(df) < 2:
            return {"status": "not_enough_bars", "symbol": symbol}
        next_bar = df.iloc[-1]
        exit_date = df.index[-1].date().isoformat()
    else:
        i = df_idx.index(entry_date)
        if i + 1 >= len(df):
            return {"status": "no_next_day_yet", "symbol": symbol}
        next_bar = df.iloc[i + 1]
        exit_date = df.index[i + 1].date().isoformat()

    high = float(next_bar["High"])
    low = float(next_bar["Low"])
    close = float(next_bar["Close"])

    if low <= sl:
        exit_price = sl
        reason = "STOP_LOSS"
    elif high >= target:
        exit_price = target
        reason = "TARGET"
    else:
        exit_price = close
        reason = "CLOSE"

    pnl = (exit_price - entry) * qty
    pnl_pct = (exit_price - entry) / entry * 100 if entry > 0 else 0.0

    # Update capital
    cap = get_capital()
    cap_new = cap + pnl
    set_capital(cap_new)

    # Append to CSV
    df_tr = pd.read_csv(TRADES_CSV_PATH)
    df_tr.loc[len(df_tr)] = [
        entry_date, exit_date, symbol, entry, exit_price, qty, pnl, pnl_pct, reason
    ]
    df_tr.to_csv(TRADES_CSV_PATH, index=False)

    clear_open_trade()

    return {
        "status": "closed",
        "symbol": symbol,
        "entry_date": entry_date,
        "exit_date": exit_date,
        "entry": round(entry, 2),
        "exit": round(exit_price, 2),
        "qty": qty,
        "pnl": round(pnl, 2),
        "pnl_pct": round(pnl_pct, 2),
        "exit_reason": reason,
        "capital_after": round(cap_new, 2)
    }
