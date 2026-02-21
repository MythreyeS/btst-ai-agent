from agents.market_regime import get_market_regime
from agents.stock_selector import select_stocks
from agents.scoring_agent import score_stocks
from telegram import send_btst_alert


def main():

    regime_data = get_market_regime()

    index = regime_data["index"]
    close = regime_data["close"]
    sma = regime_data["sma"]
    regime = regime_data["regime"]

    candidates = select_stocks(regime)
    scored = score_stocks(candidates)

    capital = 50000

    send_btst_alert(index, close, sma, regime, capital, scored)


if __name__ == "__main__":
    main()
