import yfinance as yf
import pandas as pd


def get_nifty500_symbols():

    # NSE official CSV URL (works without login)
    url = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"

    df = pd.read_csv(url)

    symbols = df["Symbol"].tolist()

    # Add .NS suffix
    symbols = [symbol + ".NS" for symbol in symbols]

    return symbols


def select_stocks(regime):

    symbols = get_nifty500_symbols()

    selected = []

    for symbol in symbols:

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

            # Liquidity filter
            if volume < 200000:
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
