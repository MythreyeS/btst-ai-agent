import json
import os

CAPITAL_FILE = "data/capital.json"

DEFAULT_CAPITAL = 10000
RISK_PER_TRADE = 0.02  # 2% risk


def initialize_capital():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(CAPITAL_FILE):
        data = {
            "capital": DEFAULT_CAPITAL
        }
        with open(CAPITAL_FILE, "w") as f:
            json.dump(data, f)


def get_capital():
    initialize_capital()

    with open(CAPITAL_FILE, "r") as f:
        data = json.load(f)

    return data["capital"]


def update_capital(new_capital):
    data = {"capital": new_capital}

    with open(CAPITAL_FILE, "w") as f:
        json.dump(data, f)


def position_size(entry_price, stop_loss):
    capital = get_capital()

    risk_amount = capital * RISK_PER_TRADE
    risk_per_share = abs(entry_price - stop_loss)

    if risk_per_share == 0:
        return 0

    quantity = int(risk_amount / risk_per_share)

    return max(quantity, 0)
