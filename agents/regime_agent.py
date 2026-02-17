import yfinance as yf
import pandas as pd

def market_regime() -> str:
    """
    Simple regime:
    BULLISH if NIFTY 50 close > SMA50
    else BEARISH
    """
    df = yf.download("^NSEI", period="6mo", interval="1d", progress=False)
    if df is None or df.empty or len(df) < 60:
        return "UNKNOWN"
    df["SMA50"] = df["Close"].rolling(50).mean()
    last = df.iloc[-1]
    if pd.isna(last["SMA50"]):
        return "UNKNOWN"
    return "BULLISH" if last["Close"] > last["SMA50"] else "BEARISH"
