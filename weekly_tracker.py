import os
import json
import pandas as pd
from datetime import datetime
from telegram import send_message

WEEKLY_FILE = "data/weekly_performance.json"
WEEKLY_REPORT_CSV = "data/weekly_report.csv"
WEEKLY_TARGET = 20000


def _init_week():
    return {
        "week_start": datetime.now().strftime("%Y-%m-%d"),
        "capital_start": 0,
        "total_pnl": 0,
        "trades": 0,
        "target_hit": False
    }


def load_week():
    if not os.path.exists(WEEKLY_FILE):
        week = _init_week()
        save_week(week)
        return week

    with open(WEEKLY_FILE, "r") as f:
        return json.load(f)


def save_week(data):
    with open(WEEKLY_FILE, "w") as f:
        json.dump(data, f, indent=4)


def update_weekly_performance(pnl, capital):
    week = load_week()

    week["total_pnl"] += pnl
    week["trades"] += 1

    if week["capital_start"] == 0:
        week["capital_start"] = capital

    # 🔥 Target Alert
    if week["total_pnl"] >= WEEKLY_TARGET and not week["target_hit"]:
        week["target_hit"] = True
        send_message(
            f"🔥 WEEKLY TARGET HIT!\n\n"
            f"Target: ₹{WEEKLY_TARGET}\n"
            f"Current PnL: ₹{week['total_pnl']}"
        )

    save_week(week)
    export_weekly_report(week)


def export_weekly_report(week):
    df = pd.DataFrame([week])
    df.to_csv(WEEKLY_REPORT_CSV, index=False)


def reset_if_new_week():
    week = load_week()
    week_start = datetime.strptime(week["week_start"], "%Y-%m-%d")

    if datetime.now().isocalendar()[1] != week_start.isocalendar()[1]:
        save_week(_init_week())
