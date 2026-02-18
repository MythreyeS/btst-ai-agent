import pandas as pd
import ta


# ==========================================================
# RSI AGENT
# Used for:
# - Live BTST decision
# - Backtesting engine
# - Multi-agent voting system
# ==========================================================


def rsi_signal(data: pd.DataFrame, period: int = 14) -> int:
    """
    Returns:
        1 -> Bullish
        0 -> Neutral / Bearish
    """

    if data is None or len(data) < period + 2:
        return 0

    try:
        close = data["Close"]

        rsi_indicator = ta.momentum.RSIIndicator(close, window=period)
        rsi_series = rsi_indicator.rsi()

        latest_rsi = rsi_series.iloc[-1]

        # BTST bullish bias logic
        if latest_rsi > 55:
            return 1
        else:
            return 0

    except Exception as e:
        print(f"[RSI AGENT ERROR]: {e}")
        return 0


# ==========================================================
# BACKWARD COMPATIBILITY
# Some files import rsi_score instead of rsi_signal
# ==========================================================

def rsi_score(data: pd.DataFrame) -> int:
    return rsi_signal(data)
