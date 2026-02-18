import yfinance as yf
import numpy as np

def consolidation_signal(symbol):
    try:
        data = yf.download(symbol, period="1mo", interval="1d", progress=False)

        high = data["High"].max()
        low = data["Low"].min()

        range_pct = (high - low) / low * 100

        if range_pct < 5:
            return 1
        else:
            return 0

    except:
        return 0
