import yfinance as yf

def get_market_regime():

    ticker = yf.Ticker("^NSEI")
    data = ticker.history(period="3mo")

    close = round(data["Close"].iloc[-1], 2)
    sma = round(data["Close"].rolling(20).mean().iloc[-1], 2)

    if close > sma:
        regime = "BULLISH"
    elif close < sma:
        regime = "BEARISH"
    else:
        regime = "NEUTRAL"

    return {
        "index": "NIFTY 50",
        "close": close,
        "sma": sma,
        "regime": regime
    }
