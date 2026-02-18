import json
import os

CAPITAL_FILE = "data/capital.json"

def initialize_capital():
    if not os.path.exists("data"):
        os.makedirs("data")

    if not os.path.exists(CAPITAL_FILE):
        with open(CAPITAL_FILE, "w") as f:
            json.dump({"current_capital": 10000}, f)

def get_capital():
    initialize_capital()
    with open(CAPITAL_FILE, "r") as f:
        data = json.load(f)
    return data["current_capital"]

def update_capital(new_value):
    with open(CAPITAL_FILE, "w") as f:
        json.dump({"current_capital": new_value}, f)

def calculate_position_size(capital, risk_percent, entry, stop):
    risk_amount = capital * risk_percent
    per_share_risk = abs(entry - stop)
    if per_share_risk == 0:
        return 0
    quantity = int(risk_amount / per_share_risk)
    return quantity
