import json
import os
from datetime import datetime

TRADES_FILE = "data/open_trade.json"


def initialize_trade_file():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(TRADES_FILE):
        with open(TRADES_FILE, "w") as f:
            json.dump({}, f)


def has_open_trade():
    initialize_trade_file()

    with open(TRADES_FILE, "r") as f:
        data = json.load(f)

    return bool(data)


def save_open_trade(symbol, entry_price, sl, target, quantity):
    trade = {
        "symbol": symbol,
        "entry_price": entry_price,
        "stop_loss": sl,
        "target": target,
        "quantity": quantity,
        "entry_date": str(datetime.today().date())
    }

    with open(TRADES_FILE, "w") as f:
        json.dump(trade, f)

    print(f"Trade saved: {trade}")


def close_trade_if_due(current_price):
    initialize_trade_file()

    with open(TRADES_FILE, "r") as f:
        trade = json.load(f)

    if not trade:
        return None

    entry = trade["entry_price"]
    sl = trade["stop_loss"]
    target = trade["target"]
    qty = trade["quantity"]

    pnl = 0
    closed = False

    if current_price <= sl:
        pnl = (sl - entry) * qty
        closed = True

    elif current_price >= target:
        pnl = (target - entry) * qty
        closed = True

    if closed:
        print(f"Trade closed. PnL: {pnl}")

        # clear trade
        with open(TRADES_FILE, "w") as f:
            json.dump({}, f)

        return pnl

    return None
