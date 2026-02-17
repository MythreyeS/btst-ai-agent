import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

from core.universe_manager import fetch_nifty200_dynamic
from core.indicators import atr
from agents.rsi_agent import rsi_score
from agents.consolidation_agent import consolidation_score
from agents.gap_agent import gap_probability_score
from agents.liquidity_agent import liquidity_score
from agents.voting_agent import combine_scores, DEFAULT_WEIGHTS
from core.utils import load_json
from capital_manager import set_capital

def run_backtest(lookback_days: int = 60, start_capital: float = 10000.0, universe_limit: int = 120) -> dict:
    """
    Daily loop (no-lookahead):
    - Each day selects best stock using data up to that day.
    - Entry at Close (day t)
    - Exit on next day using OHLC rule: SL/Target/Close
    """
    set_capital(start_capital)
    policy = load_json("data/policy.json", {"weights": DEFAULT_WEIGHTS})
    weights = policy.get("weights", DEFAULT_WEIGHTS)

    symbols = fetch_nifty200_dynamic(cache_path="data/nifty200.csv")[:universe_limit]

    end = datetime.now().date()
    start = end - timedelta(days=int(lookback_days * 2))  # buffer for non-trading days
    start_str = start.isoformat()
    end_str = end.isoformat()

    # Download all symbols (slow if too many; universe_limit keeps it sane)
    data_map = {}
    for sym in symbols:
        df = yf.download(sym, start=start_str, end=end_str, interval="1d", progress=False)
        if df is not None and not df.empty and len(df) > 30:
            df = df.dropna().copy()
            df["ATR"] = atr(df, 14)
            data_map[sym] = df

    # Find common trading dates
    all_dates = None
    for df in data_map.values():
        idx = df.index
        all_dates = idx if all_dates is None else all_dates.intersection(idx)
    if all_dates is None or len(all_dates) < 20:
        return {"status": "insufficient_data"}

    all_dates = sorted(list(all_dates))
    # keep last N trading days
    if len(all_dates) > lookback_days + 5:
        all_dates = all_dates[-(lookback_days + 5):]

    trades = []
    capital = start_capital

    for i in range(len(all_dates) - 1):
        d = all_dates[i]
        next_d = all_dates[i + 1]

        # build best pick for date d
        best = None
        best_score = -1

        for sym, df in data_map.items():
            if d not in df.index or next_d not in df.index:
                continue
            sub = df.loc[:d].copy()
            if len(sub) < 60:
                continue

            scores = {
                "rsi": rsi_score(sub),
                "consolidation": consolidation_score(sub),
                "gap": gap_probability_score(sub),
                "liquidity": liquidity_score(sub),
            }

            if scores["liquidity"] <= 0 or scores["rsi"] <= 0:
                continue

            final, votes = combine_scores(scores, weights)
            if final > best_score:
                best_score = final
                last = sub.iloc[-1]
                best = (sym, last, scores, votes, final)

        if not best:
            continue

        sym, last, scores, votes, final = best
        entry = float(last["Close"])
        atr_val = float(last["ATR"]) if pd.notna(last["ATR"]) else entry * 0.02

        sl = entry - atr_val
        target = entry + (atr_val * 1.8)

        # next day exit
        nb = data_map[sym].loc[next_d]
        high = float(nb["High"])
        low = float(nb["Low"])
        close = float(nb["Close"])

        if low <= sl:
            exit_price = sl
            reason = "STOP_LOSS"
        elif high >= target:
            exit_price = target
            reason = "TARGET"
        else:
            exit_price = close
            reason = "CLOSE"

        # 1% risk sizing
        risk_amt = capital * 0.01
        risk_per_share = abs(entry - sl)
        qty = int(risk_amt / risk_per_share) if risk_per_share > 0 else 0
        qty = max(qty, 0)

        pnl = (exit_price - entry) * qty
        capital += pnl

        trades.append({
            "entry_date": d.date().isoformat(),
            "exit_date": next_d.date().isoformat(),
            "symbol": sym,
            "entry": round(entry, 2),
            "exit": round(exit_price, 2),
            "qty": qty,
            "pnl": round(pnl, 2),
            "exit_reason": reason,
            "final_score": round(float(final), 4),
            "scores": {k: round(float(v), 4) for k, v in scores.items()},
            "votes": votes
        })

    df_tr = pd.DataFrame(trades)
    if not df_tr.empty:
        df_tr.to_csv("data/backtest_trades.csv", index=False)

    return {
        "status": "ok",
        "trades": int(len(trades)),
        "start_capital": float(start_capital),
        "end_capital": float(round(capital, 2)),
        "net_pnl": float(round(capital - start_capital, 2)),
        "backtest_csv": "data/backtest_trades.csv" if not df_tr.empty else None
    }
