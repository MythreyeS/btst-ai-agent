import yfinance as yf
import pandas as pd
from core.indicators import flatten_columns, rsi, atr, pct_change, is_consolidating, close_near_high

def build_features(symbol: str) -> dict | None:
    """
    Perception Agent: pulls data + computes features for the Strategy Agent.
    """
    try:
        df = yf.download(symbol + ".NS", period="3mo", progress=False)
        if df is None or df.empty or len(df) < 60:
            return None

        df = flatten_columns(df)

        df["RSI"] = rsi(df)
        df["ATR"] = atr(df)
        df["VOL20"] = df["Volume"].rolling(20).mean()
        df["DMA50"] = df["Close"].rolling(50).mean()
        df["HIGH20"] = df["High"].rolling(20).max()

        latest = df.iloc[-1]
        prev = df.iloc[-2]

        close = float(latest["Close"])
        open_ = float(latest["Open"])
        high = float(latest["High"])
        low = float(latest["Low"])
        vol = float(latest["Volume"])
        vol20 = float(df["VOL20"].iloc[-1]) if pd.notna(df["VOL20"].iloc[-1]) else 0.0

        features = {
            "symbol": symbol,
            "close": close,
            "open": open_,
            "high": high,
            "low": low,
            "rsi": float(latest["RSI"]),
            "atr": float(latest["ATR"]) if pd.notna(latest["ATR"]) else 0.0,
            "vol_ratio": (vol / vol20) if vol20 > 0 else 0.0,
            "trend_50dma": 1.0 if (pd.notna(latest["DMA50"]) and close > float(latest["DMA50"])) else 0.0,
            "breakout_20": 1.0 if (pd.notna(df["HIGH20"].iloc[-2]) and close > float(df["HIGH20"].iloc[-2])) else 0.0,
            "mom_1d": pct_change(df["Close"], 1),
            "mom_5d": pct_change(df["Close"], 5),
            "strong_close": 1.0 if close > open_ else 0.0,
            "close_near_high": 1.0 if close_near_high(df, 0.7) else 0.0,
            "consolidating": 1.0 if is_consolidating(df, 10, 0.05) else 0.0,
        }

        # basic liquidity guard (agent perception)
        features["liquid"] = 1.0 if vol20 >= 500000 else 0.0

        return features

    except Exception:
        return None
