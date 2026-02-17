import pandas as pd
import numpy as np

def rsi(close: pd.Series, period: int = 14) -> pd.Series:
    delta = close.diff()
    gain = delta.where(delta > 0, 0.0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - (100 / (1 + rs))

def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high = df["High"]
    low = df["Low"]
    close = df["Close"]
    prev_close = close.shift(1)

    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    return tr.rolling(period).mean()

def is_consolidating(df: pd.DataFrame, days: int = 10, threshold: float = 0.03) -> bool:
    recent = df.tail(days)
    if len(recent) < days:
        return False
    max_close = recent["Close"].max()
    min_close = recent["Close"].min()
    if min_close <= 0:
        return False
    return (max_close - min_close) / min_close < threshold
