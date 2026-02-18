import csv
import os
from capital_manager import update_capital

FILE = "data/weekly_performance.csv"

def update_weekly_performance(result, pnl):

    if not os.path.exists("data"):
        os.makedirs("data")

    write_header = not os.path.exists(FILE)

    with open(FILE, "a", newline="") as f:
        writer = csv.writer(f)

        if write_header:
            writer.writerow(["Result", "PnL"])

        writer.writerow([result, pnl])

    from capital_manager import get_capital
    capital = get_capital()
    update_capital(capital + pnl)
