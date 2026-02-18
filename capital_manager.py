import json
import os

CAPITAL_FILE = "data/capital.json"


def _ensure_file():
    if not os.path.exists("data"):
        os.makedirs("data")

    if not os.path.exists(CAPITAL_FILE):
        with open(CAPITAL_FILE, "w") as f:
            json.dump({
                "current_capital": 100000,
                "weekly_target": 20000
            }, f)


def get_capital():
    _ensure_file()

    with open(CAPITAL_FILE, "r") as f:
        data = json.load(f)

    return data.get("current_capital", 100000)


def set_capital(new_capital):
    _ensure_file()

    with open(CAPITAL_FILE, "r") as f:
        data = json.load(f)

    data["current_capital"] = new_capital

    with open(CAPITAL_FILE, "w") as f:
        json.dump(data, f, indent=4)


def position_size(entry_price, risk_percent=0.02):
    capital = get_capital()
    risk_amount = capital * risk_percent
    quantity = int(risk_amount / entry_price)
    return max(quantity, 1)
