import pandas as pd

def liquidity_score(df: pd.DataFrame, min_volume: int = 500000) -> float:
    """
    Very simple liquidity score using latest volume.
    """
    if df is None or df.empty:
        return 0.0
    v = float(df["Volume"].iloc[-1])
    if v <= 0:
        return 0.0
    if v < min_volume:
        return 0.0
    # score saturates at 3x min_volume
    cap = min(v, 3 * min_volume)
    return (cap - min_volume) / (2 * min_volume)
