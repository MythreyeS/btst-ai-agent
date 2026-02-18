import yfinance as yf
import pandas as pd

def market_regime():
    """
    Market regime using NIFTY index and 50 SMA
    """

    print("Checking market regime...")

    data = yf.download("^NSEI", period="6mo", interval="1d", progress=False)

    data["SMA50"] = data["Close"].rolling(50).mean()

    last_close = float(data["Close"].iloc[-1])
    last_sma50 = float(data["SMA50"].iloc[-1])

    print(f"Nifty Close: {last_close}")
    print(f"Nifty SMA50: {last_sma50}")

    if last_close > last_sma50:
        print("Market Regime: BULLISH")
        return "BULLISH"
    else:
        print("Market Regime: BEARISH")
        return "BEARISH"
