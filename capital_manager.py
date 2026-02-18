import json
import os

CAPITAL_FILE = "data/capital.json"

DEFAULT_CAPITAL = {
    "initial_capital": 10000,
    "current_capital": 10000,
    "weekly_target": 20000,
    "risk_per_trade": 0.02
}


def _ensure_file():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(CAPITAL_FILE):
        with open(CAPITAL_FILE, "w") as f:
            json.dump(DEFAULT_CAPITAL, f, indent=4)


def _load():
    _ensure_file()
    with open(CAPITAL_FILE, "r") as f:
        return json.load(f)


def _save(data):
    with open(CAPITAL_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ============================
# CAPITAL ACCESS
# ============================

def get_capital():
    data = _load()
    return data["current_capital"]


def set_capital(new_capital):
    data = _load()
    data["current_capital"] = float(new_capital)
    _save(data)


def update_capital(pnl):
    data = _load()
    data["current_capital"] += float(pnl)
    _save(data)


# ============================
# POSITION SIZING
# ============================

def calculate_position_size(entry_price, stop_loss, risk_percent=None):
    data = _load()

    capital = data["current_capital"]

    if risk_percent is None:
        risk_percent = data.get("risk_per_trade", 0.02)

    risk_amount = capital * risk_percent

    risk_per_share = abs(entry_price - stop_loss)

    if risk_per_share == 0:
        return 1

    quantity = int(risk_amount / risk_per_share)

    return max(quantity, 1)


# ============================
# WEEKLY TARGET CHECK
# ============================

def weekly_target_reached():
    data = _load()
    profit = data["current_capital"] - data["initial_capital"]

    return profit >= data["weekly_target"]
