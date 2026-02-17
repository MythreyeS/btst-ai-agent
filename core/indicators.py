import numpy as np
import pandas as pd

def flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

def rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    close = df["Close"].astype(float)
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    out = 100 - (100 / (1 + rs))
    return out.fillna(0)

def atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high = df["High"].astype(float)
    low = df["Low"].astype(float)
    close = df["Close"].astype(float)
    tr = pd.concat([
        (high - low),
        (high - close.shift(1)).abs(),
        (low - close.shift(1)).abs()
    ], axis=1).max(axis=1)
    return tr.rolling(period).mean()

def pct_change(series: pd.Series, n: int = 1) -> float:
    if len(series) < n + 1:
        return 0.0
    prev = float(series.iloc[-(n+1)])
    cur = float(series.iloc[-1])
    if prev == 0:
        return 0.0
    return (cur - prev) / prev

def is_consolidating(df: pd.DataFrame, lookback: int = 10, max_range_pct: float = 0.05) -> bool:
    if len(df) < lookback + 5:
        return False
    recent = df.tail(lookback)
    hi = float(recent["High"].max())
    lo = float(recent["Low"].min())
    if lo <= 0:
        return False
    return ((hi - lo) / lo) <= max_range_pct

def close_near_high(df: pd.DataFrame, threshold: float = 0.7) -> bool:
    latest = df.iloc[-1]
    c = float(latest["Close"]); h = float(latest["High"]); l = float(latest["Low"])
    rng = max(h - l, 1e-9)
    pos = (c - l) / rng
    return pos >= threshold
