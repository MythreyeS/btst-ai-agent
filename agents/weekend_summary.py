import yfinance as yf
from datetime import datetime, timedelta

def get_last_friday_data():

    ticker = yf.Ticker("^NSEI")
    data = ticker.history(period="7d")

    # Get last available close (Friday)
    friday_close = round(data["Close"].iloc[-1], 2)
    friday_sma = round(data["Close"].rolling(20).mean().iloc[-1], 2)

    if friday_close > friday_sma:
        regime = "BULLISH"
    elif friday_close < friday_sma:
        regime = "BEARISH"
    else:
        regime = "NEUTRAL"

    return {
        "close": friday_close,
        "sma": friday_sma,
        "regime": regime
    }
