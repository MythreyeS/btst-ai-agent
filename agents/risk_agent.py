from core.storage import load_json
from capital_manager import load_capital

WEEKLY_FILE = "data/weekly.json"

def compute_risk_pct(agent_score: float, regime_multiplier: float) -> float:
    """
    Aggressive mode:
    - base risk 2%
    - scale to 3% if confidence very high
    - reduce if regime is weaker
    """
    base = 0.02
    if agent_score >= 0.75:
        base = 0.03
    elif agent_score >= 0.68:
        base = 0.025

    risk = base * regime_multiplier
    # clamp 1%..3.5%
    return max(0.01, min(risk, 0.035))

def position_size(entry: float, sl: float, risk_amount: float) -> int:
    per_share_risk = max(entry - sl, 0.01)
    qty = int(risk_amount / per_share_risk)
    return max(qty, 1)

def current_week_pnl() -> float:
    data = load_json(WEEKLY_FILE, {})
    # best effort: take max week key
    if not data:
        return 0.0
    try:
        last_week = sorted(data.keys())[-1]
        return float(data.get(last_week, 0.0))
    except Exception:
        return 0.0
