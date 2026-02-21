import yfinance as yf

NIFTY_STOCKS = [
    "RELIANCE.NS",
    "HDFCBANK.NS",
    "INFY.NS",
    "ICICIBANK.NS",
    "TCS.NS"
]

def select_stocks(regime):

    selected = []

    for symbol in NIFTY_STOCKS:
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="3mo")

            if len(data) < 50:
                continue

            close = data["Close"].iloc[-1]
            sma50 = data["Close"].rolling(50).mean().iloc[-1]
            volume = data["Volume"].iloc[-1]

            # Regime filter
            if regime == "BULLISH" and close < sma50:
                continue
            if regime == "BEARISH" and close > sma50:
                continue

            if volume < 1000000:
                continue

            atr = (data["High"] - data["Low"]).rolling(14).mean().iloc[-1]
            volatility = data["Close"].pct_change().std()

            selected.append({
                "symbol": symbol,
                "current_price": round(close, 2),
                "entry_price": round(close, 2),
                "atr": round(atr, 2),
                "volatility": round(volatility, 4)
            })

        except Exception:
            continue

    return selected
