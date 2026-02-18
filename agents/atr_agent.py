import yfinance as yf
import pandas as pd

def calculate_atr(symbol):
    data = yf.download(symbol, period="3mo", interval="1d", progress=False)

    high_low = data["High"] - data["Low"]
    high_close = abs(data["High"] - data["Close"].shift())
    low_close = abs(data["Low"] - data["Close"].shift())

    ranges = pd.concat([high_low, high_close, low_close], axis=1)
    true_range = ranges.max(axis=1)
    atr = true_range.rolling(14).mean()

    return float(atr.iloc[-1])

def atr_levels(symbol):
    data = yf.download(symbol, period="5d", interval="1d", progress=False)
    last_close = float(data["Close"].iloc[-1])
    atr = calculate_atr(symbol)

    stop = last_close - atr
    target = last_close + (2 * atr)

    return last_close, stop, target
