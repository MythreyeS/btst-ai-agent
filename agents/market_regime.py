import yfinance as yf


def get_market_regime():
    nifty = yf.Ticker("^NSEI")
    df = nifty.history(period="3mo", interval="1d")

    if df is None or df.empty or len(df) < 30:
        return {
            "index": "NIFTY 50",
            "close": None,
            "sma20": None,
            "sma50": None,
            "regime": "NEUTRAL"
        }

    close = float(df["Close"].iloc[-1])
    sma20 = float(df["Close"].rolling(20).mean().iloc[-1])
    sma50 = float(df["Close"].rolling(50).mean().iloc[-1]) if len(df) >= 50 else float(df["Close"].rolling(20).mean().iloc[-1])

    if close > sma20 and close > sma50:
        regime = "BULLISH"
    elif close < sma20 and close < sma50:
        regime = "BEARISH"
    else:
        regime = "NEUTRAL"

    return {
        "index": "NIFTY 50",
        "close": round(close, 2),
        "sma20": round(sma20, 2),
        "sma50": round(sma50, 2),
        "regime": regime
    }
