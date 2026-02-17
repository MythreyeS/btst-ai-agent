import pandas as pd
import numpy as np


def calculate_rsi(data, period=14):
    """
    Standard RSI calculation.
    Returns RSI series.
    """

    delta = data["Close"].diff()

    gain = np.where(delta > 0, delta, 0)
    loss = np.where(delta < 0, -delta, 0)

    avg_gain = pd.Series(gain).rolling(period).mean()
    avg_loss = pd.Series(loss).rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def rsi_score(data):
    """
    Returns BTST-friendly RSI score.

    Score Logic:
        3 → Strong momentum (RSI 55–70)
        2 → Mild bullish (RSI 50–55)
        1 → Neutral (45–50)
        0 → Weak / avoid
    """

    if len(data) < 20:
        return 0

    rsi = calculate_rsi(data)
    latest_rsi = rsi.iloc[-1]

    if 55 <= latest_rsi <= 70:
        return 3

    elif 50 <= latest_rsi < 55:
        return 2

    elif 45 <= latest_rsi < 50:
        return 1

    else:
        return 0
