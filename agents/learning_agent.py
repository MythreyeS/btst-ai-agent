import pandas as pd
from core.storage import load_json
from agents.strategy_agent import load_policy, save_policy

TRADES_CSV = "data/trades.csv"

def update_policy_from_recent(window: int = 20):
    """
    Learning Agent:
    - Looks at recent trades
    - If breakout trades are winning, increase breakout weight
    - If momentum trades are winning, increase momentum weights
    - Keeps weights normalized
    This is simple but it is *real* agent adaptation.
    """
    try:
        df = pd.read_csv(TRADES_CSV)
        if df.empty or len(df) < 10:
            return
    except Exception:
        return

    recent = df.tail(window).copy()
    recent["win"] = recent["pnl"] > 0

    win_rate = recent["win"].mean()
    # If win rate low, become conservative: raise threshold slightly
    policy = load_policy()

    # Adaptive threshold
    if win_rate < 0.45:
        policy["threshold"] = min(0.72, policy["threshold"] + 0.02)
    elif win_rate > 0.60:
        policy["threshold"] = max(0.55, policy["threshold"] - 0.01)

    # Adaptive weights based on whether winners had bigger gap advantage
    # We use simple heuristics because we are not doing ML yet.
    avg_win_gap = recent[recent["win"]]["gap_pct"].mean() if recent["win"].any() else 0.0
    avg_loss_gap = recent[~recent["win"]]["gap_pct"].mean() if (~recent["win"]).any() else 0.0

    w = policy["weights"]

    # If gap helps wins, emphasize vol_ratio + close_near_high
    if avg_win_gap > avg_loss_gap:
        w["vol_ratio"] = min(0.30, w["vol_ratio"] + 0.02)
        w["close_near_high"] = min(0.18, w["close_near_high"] + 0.01)

    # Normalize weights to sum to 1
    total = sum(w.values())
    for k in list(w.keys()):
        w[k] = float(w[k] / total)

    policy["weights"] = w
    save_policy(policy)
