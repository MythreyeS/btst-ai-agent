import pandas as pd
import numpy as np


def calculate_rsi(series, period=14):
    """
    Calculate RSI indicator
    """
    delta = series.diff()

    gain = delta.clip(lower=0)
    loss = -1 * delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def rsi_signal(data):
    """
    Returns score based on RSI level
    """

    rsi = calculate_rsi(data["Close"])

    latest_rsi = rsi.iloc[-1]

    if np.isnan(latest_rsi):
        return 0

    # 🔥 BTST Logic:
    # 40–60 neutral accumulation zone
    # 50–65 strong continuation zone

    if 45 <= latest_rsi <= 60:
        return 3   # Strong signal
    elif 40 <= latest_rsi < 45:
        return 2
    elif 60 < latest_rsi <= 65:
        return 2
    else:
        return 0
