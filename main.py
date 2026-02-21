from datetime import datetime
from agents.market_regime import get_market_regime
from agents.stock_selector import select_stocks
from agents.scoring_agent import score_stocks
from agents.weekend_summary import get_last_friday_data
from telegram import send_btst_alert, send_weekend_summary


def main():

    today = datetime.now().weekday()  # 0=Mon, 6=Sun

    capital = 50000

    # Saturday (5) or Sunday (6)
    if today in [5, 6]:
        friday_data = get_last_friday_data()

        send_weekend_summary(
            friday_data["close"],
            friday_data["sma"],
            friday_data["regime"]
        )

    else:
        regime_data = get_market_regime()

        candidates = select_stocks(regime_data["regime"])
        scored = score_stocks(candidates)

        send_btst_alert(
            regime_data["index"],
            regime_data["close"],
            regime_data["sma"],
            regime_data["regime"],
            capital,
            scored
        )


if __name__ == "__main__":
    main()
