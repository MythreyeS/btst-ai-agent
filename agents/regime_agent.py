import yfinance as yf
import pandas as pd


def get_market_regime():
    symbol = "^NSEI"  # Nifty 50

    data = yf.download(symbol, period="3mo", interval="1d", progress=False)

    if data.empty:
        return "UNKNOWN", 0, 0

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    close = float(data["Close"].iloc[-1])
    sma20 = float(data["Close"].rolling(20).mean().iloc[-1])

    threshold = 0.003  # 0.3%

    diff = (close - sma20) / sma20

    if diff > 0.002:  # 0.2% above SMA
        regime = "BULLISH"
    elif diff < -threshold:
        regime = "BEARISH"
    else:
        regime = "NEUTRAL"

    return regime, close, sma20
