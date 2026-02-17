import numpy as np


def consolidation_signal(data, lookback=10, threshold=0.04):
    """
    Detects price consolidation phase.

    Returns:
        3 -> Strong consolidation (tight range)
        2 -> Moderate consolidation
        0 -> No consolidation
    """

    if len(data) < lookback:
        return 0

    recent = data.tail(lookback)

    highest = recent["High"].max()
    lowest = recent["Low"].min()

    range_pct = (highest - lowest) / lowest

    # 🔥 Tight consolidation (very strong breakout setup)
    if range_pct < threshold:
        return 3

    # Moderate consolidation
    elif range_pct < threshold * 1.5:
        return 2

    else:
        return 0
