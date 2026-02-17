from core.storage import load_json, save_json

CAPITAL_FILE = "data/capital.json"

def load_capital(default_capital: float = 10000.0) -> float:
    data = load_json(CAPITAL_FILE, {"capital": default_capital})
    return float(data.get("capital", default_capital))

def update_capital(new_capital: float) -> None:
    save_json(CAPITAL_FILE, {"capital": float(new_capital)})
