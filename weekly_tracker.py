from datetime import datetime
from core.storage import load_json, save_json
from telegram import send_message

WEEKLY_FILE = "data/weekly.json"

def add_weekly_profit(profit: float, weekly_target: float = 20000.0) -> float:
    data = load_json(WEEKLY_FILE, {})
    week_no = str(datetime.now().isocalendar()[1])
    cur = float(data.get(week_no, 0.0))
    cur += float(profit)
    data[week_no] = cur
    save_json(WEEKLY_FILE, data)

    if cur >= weekly_target:
        send_message(f"🎉 Weekly target reached!\nWeek #{week_no} P&L: ₹{cur:,.0f}")

    return cur
