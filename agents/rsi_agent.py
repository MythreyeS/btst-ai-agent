import pandas as pd
from core.indicators import rsi

def rsi_score(df: pd.DataFrame, min_rsi: float = 55.0) -> float:
    """
    Returns 0..1 score based on RSI.
    """
    if df is None or df.empty or len(df) < 30:
        return 0.0
    df = df.copy()
    df["RSI"] = rsi(df["Close"], 14)
    val = float(df["RSI"].iloc[-1])
    if pd.isna(val):
        return 0.0
    # score grows from min_rsi to 75
    if val < min_rsi:
        return 0.0
    capped = min(val, 75.0)
    return (capped - min_rsi) / (75.0 - min_rsi)
