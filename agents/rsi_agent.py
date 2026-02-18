import yfinance as yf
import pandas as pd

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def rsi_signal(symbol):
    try:
        data = yf.download(symbol, period="3mo", interval="1d", progress=False)

        rsi = calculate_rsi(data["Close"])

        latest_rsi = float(rsi.iloc[-1])

        if latest_rsi > 55 and latest_rsi < 70:
            return 1
        else:
            return 0

    except:
        return 0
