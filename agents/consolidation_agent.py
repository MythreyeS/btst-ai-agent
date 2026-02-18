import yfinance as yf
import pandas as pd


def consolidation_score(symbol, lookback=20):
    """
    Returns a consolidation score between 0 and 1
    Higher score = tighter range (good for breakout setups)
    """

    try:
        data = yf.download(symbol, period="3mo", progress=False)

        if len(data) < lookback:
            return 0

        recent = data.tail(lookback)

        high = recent["High"].max()
        low = recent["Low"].min()

        range_pct = (high - low) / low

        # Smaller range = stronger consolidation
        if range_pct < 0.03:
            return 1.0
        elif range_pct < 0.05:
            return 0.8
        elif range_pct < 0.08:
            return 0.5
        else:
            return 0.2

    except Exception as e:
        print(f"Consolidation error for {symbol}: {e}")
        return 0
