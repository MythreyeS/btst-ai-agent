import yfinance as yf
import pandas as pd

def market_regime():
    symbol = "^NSEI"  # Nifty 50

    df = yf.download(symbol, period="6mo", interval="1d")

    if df.empty:
        return "neutral"

    df["SMA50"] = df["Close"].rolling(50).mean()

    # get last row safely as scalar
    last_close = df["Close"].iloc[-1]
    last_sma50 = df["SMA50"].iloc[-1]

    if pd.isna(last_sma50):
        return "neutral"

    if last_close > last_sma50:
        return "bullish"
    else:
        return "bearish"
