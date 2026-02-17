import os
import pandas as pd
from datetime import datetime
from core.utils import load_json, save_json, ensure_dir
from capital_manager import get_capital

WEEKLY_JSON = "data/weekly.json"
PERF_WEEKLY_CSV = "data/performance_weekly.csv"
TRADES_CSV = "data/trades.csv"

def _week_key(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    year, week, _ = dt.isocalendar()
    return f"{year}-W{week:02d}"

def update_weekly_performance():
    ensure_dir("data")

    if not os.path.exists(TRADES_CSV):
        # nothing to update yet
        return {"status": "no_trades"}

    trades = pd.read_csv(TRADES_CSV)
    if trades.empty:
        return {"status": "no_trades"}

    # Weekly aggregation by exit_date
    trades["exit_date"] = trades["exit_date"].astype(str)
    trades["week"] = trades["exit_date"].apply(_week_key)

    agg = trades.groupby("week").agg(
        trades=("symbol", "count"),
        pnl=("pnl", "sum"),
        avg_pnl=("pnl", "mean"),
        win_rate=("pnl", lambda s: float((s > 0).mean()) * 100.0),
    ).reset_index()

    agg.to_csv(PERF_WEEKLY_CSV, index=False)

    weekly = load_json(WEEKLY_JSON, {"target_weekly_profit": 20000, "hits": {}})
    hits = weekly.get("hits", {})

    # store latest week summary
    latest_week = agg.iloc[-1].to_dict()
    hits[str(latest_week["week"])] = {
        "trades": int(latest_week["trades"]),
        "pnl": float(latest_week["pnl"]),
        "win_rate": float(latest_week["win_rate"]),
        "capital": float(get_capital())
    }

    weekly["hits"] = hits
    save_json(WEEKLY_JSON, weekly)

    return {"status": "updated", "latest_week": latest_week}
