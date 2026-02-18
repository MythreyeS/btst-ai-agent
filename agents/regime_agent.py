import yfinance as yf
import pandas as pd

def market_regime():
    symbol = "^NSEI"

    df = yf.download(symbol, period="6mo", interval="1d", auto_adjust=True)

    if df.empty:
        return "neutral"

    # Ensure Close is a proper Series
    close_series = df["Close"]

    if isinstance(close_series, pd.DataFrame):
        close_series = close_series.iloc[:, 0]

    df["SMA50"] = close_series.rolling(50).mean()

    last_close = float(close_series.iloc[-1])
    last_sma50 = float(df["SMA50"].iloc[-1])

    if pd.isna(last_sma50):
        return "neutral"

    if last_close > last_sma50:
        return "bullish"
    else:
        return "bearish"
