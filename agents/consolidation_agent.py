import yfinance as yf


def consolidation_score(symbol, lookback=20):
    """
    Returns a numeric score (0 to 1)
    Higher score = tighter range
    """

    try:
        data = yf.download(symbol, period="3mo", progress=False)

        if len(data) < lookback:
            return 0

        recent = data.tail(lookback)

        high = recent["High"].max()
        low = recent["Low"].min()

        range_pct = (high - low) / low

        if range_pct < 0.03:
            return 1.0
        elif range_pct < 0.05:
            return 0.8
        elif range_pct < 0.08:
            return 0.5
        else:
            return 0.2

    except Exception as e:
        print(f"Consolidation error for {symbol}: {e}")
        return 0


def consolidation_signal(symbol):
    """
    Returns True if strong consolidation exists
    Used by orchestrator for voting
    """

    score = consolidation_score(symbol)

    if score >= 0.8:
        return True
    else:
        return False
