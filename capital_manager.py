import json
import os

CAPITAL_FILE = "data/capital.json"


def _init_capital(initial=10000):
    return {
        "current_capital": initial,
        "starting_capital": initial
    }


def load_capital():
    if not os.path.exists(CAPITAL_FILE):
        data = _init_capital()
        save_capital(data)
        return data

    with open(CAPITAL_FILE, "r") as f:
        return json.load(f)


def save_capital(data):
    os.makedirs("data", exist_ok=True)
    with open(CAPITAL_FILE, "w") as f:
        json.dump(data, f, indent=4)


def get_capital():
    data = load_capital()
    return data["current_capital"]


def set_capital(amount):
    data = load_capital()
    data["current_capital"] = amount
    save_capital(data)


def update_capital(pnl):
    data = load_capital()
    data["current_capital"] += pnl
    save_capital(data)


def calculate_position_size(entry_price, risk_percent=2):
    """
    Risk-based position sizing.
    Risk = 2% of capital by default.
    """

    capital = get_capital()
    risk_amount = capital * (risk_percent / 100)

    if entry_price <= 0:
        return 0

    quantity = int(risk_amount / entry_price)
    return max(quantity, 1)
