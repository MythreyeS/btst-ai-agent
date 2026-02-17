import yfinance as yf
import pandas as pd
from core.indicators import flatten_columns

def market_regime() -> dict:
    """
    Regime Agent: decides if BTST is allowed and how aggressive to be.
    """
    df = yf.download("^NSEI", period="6mo", progress=False)
    if df is None or df.empty or len(df) < 60:
        return {"regime": "UNKNOWN", "allow_btst": False, "risk_multiplier": 0.5}

    df = flatten_columns(df)
    df["DMA50"] = df["Close"].rolling(50).mean()
    df["DMA200"] = df["Close"].rolling(200).mean()
    latest = df.iloc[-1]

    close = float(latest["Close"])
    dma50 = float(latest["DMA50"]) if pd.notna(latest["DMA50"]) else None
    dma200 = float(latest["DMA200"]) if pd.notna(latest["DMA200"]) else None

    if dma50 is None:
        return {"regime": "UNKNOWN", "allow_btst": False, "risk_multiplier": 0.5}

    if close > dma50 and (dma200 is None or dma50 > dma200):
        return {"regime": "BULL", "allow_btst": True, "risk_multiplier": 1.2}

    if close < dma50:
        return {"regime": "BEAR", "allow_btst": False, "risk_multiplier": 0.5}

    return {"regime": "SIDEWAYS", "allow_btst": True, "risk_multiplier": 0.8}
