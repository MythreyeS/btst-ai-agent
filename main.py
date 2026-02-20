from telegram import send_btst_alert


def main():

    index = "NIFTY 50"
    close = 25571.25
    sma = 25576.13
    regime = "NEUTRAL"
    capital = 50000

    # Example stock structure
    selected_stocks = [
        {
            "symbol": "RELIANCE.NS",
            "final_score": 69.25,
            "current_price": 2458,
            "entry_price": 2450,
            "atr": 30,
            "volatility": 0.018,
            "votes": {
                "rsi": 1,
                "consolidation": 1,
                "gap": 1,
                "liquidity": 1
            }
        }
    ]

    send_btst_alert(index, close, sma, regime, capital, selected_stocks)


if __name__ == "__main__":
    main()
