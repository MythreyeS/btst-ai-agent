import os
from core.storage import load_json, save_json

OPEN_TRADE_FILE = "data/open_trade.json"

def save_trade(trade: dict) -> None:
    save_json(OPEN_TRADE_FILE, trade)

def load_trade():
    trade = load_json(OPEN_TRADE_FILE, {})
    if not trade or "symbol" not in trade:
        return None
    return trade

def clear_trade():
    save_json(OPEN_TRADE_FILE, {})
