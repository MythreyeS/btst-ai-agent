from core.utils import load_json, save_json

CAPITAL_PATH = "data/capital.json"

def get_capital(default_capital: float = 10000.0) -> float:
    data = load_json(CAPITAL_PATH, {"capital": default_capital})
    return float(data.get("capital", default_capital))

def set_capital(value: float) -> None:
    save_json(CAPITAL_PATH, {"capital": float(value)})

def position_size(capital: float, risk_pct: float, entry: float, stop: float) -> int:
    risk_amt = capital * risk_pct
    risk_per_share = abs(entry - stop)
    if risk_per_share <= 0:
        return 0
    qty = int(risk_amt / risk_per_share)
    return max(qty, 0)
