from agents.market_regime import get_market_regime
from agents.stock_selector import select_stocks
from agents.scoring_agent import score_stocks
from telegram import send_btst_alert


def main():

    # 1️⃣ Market regime agent
    regime_data = get_market_regime()

    index = regime_data["index"]
    close = regime_data["close"]
    sma = regime_data["sma"]
    regime = regime_data["regime"]

    # 2️⃣ Universe selection agent
    candidate_stocks = select_stocks(regime)

    # 3️⃣ Scoring agent
    selected_stocks = score_stocks(candidate_stocks)

    capital = 50000  # This can also come from config

    # 4️⃣ Telegram delivery agent
    send_btst_alert(
        index=index,
        close=close,
        sma=sma,
        regime=regime,
        capital=capital,
        selected_stocks=selected_stocks
    )


if __name__ == "__main__":
    main()
