import pandas as pd
import numpy as np

def gap_probability_score(df: pd.DataFrame, lookback: int = 60) -> float:
    """
    Estimate probability that next-day open gaps up (Open_{t+1} > Close_t)
    using historical data.
    Returns 0..1.
    """
    if df is None or df.empty or len(df) < lookback + 2:
        return 0.0

    d = df.tail(lookback + 2).copy()
    # gap_next = Open_{t+1} - Close_t
    d["gap_next"] = d["Open"].shift(-1) - d["Close"]
    gaps = d["gap_next"].dropna()

    if gaps.empty:
        return 0.0

    p_up = float((gaps > 0).mean())  # probability of gap up
    # normalize: 0.45 -> 0, 0.60 -> 1 (adjust as you like)
    lo, hi = 0.45, 0.60
    score = (p_up - lo) / (hi - lo)
    return float(np.clip(score, 0.0, 1.0))
