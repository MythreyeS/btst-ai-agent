import pandas as pd
import numpy as np


def calculate_rsi(data, period=14):
    delta = data["Close"].diff()

    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = pd.Series(gain).rolling(period).mean()
    avg_loss = pd.Series(loss).rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def rsi_signal(data):
    """
    Returns BTST signal score based on RSI.
    """

    if len(data) < 20:
        return 0

    rsi = calculate_rsi(data)
    latest_rsi = rsi.iloc[-1]

    # Strong momentum zone
    if 55 <= latest_rsi <= 70:
        return 3

    # Mild bullish
    elif 50 <= latest_rsi < 55:
        return 2

    # Neutral
    elif 45 <= latest_rsi < 50:
        return 1

    # Weak / avoid
    else:
        return 0
