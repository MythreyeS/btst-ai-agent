import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from agents.regime_agent import market_regime
from capital_manager import calculate_position_size


# =========================
# CONFIGURATION
# =========================

RISK_PER_TRADE = 0.01          # 1% capital risk
MIN_VOLUME = 500000            # liquidity filter
RSI_PERIOD = 14
ATR_PERIOD = 14
RR_RATIO = 1.8                 # Reward:Risk ratio
CONSOLIDATION_DAYS = 10


# =========================
# INDICATOR FUNCTIONS
# =========================

def calculate_rsi(df, period=14):
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def calculate_atr(df, period=14):
    df['H-L'] = df['High'] - df['Low']
    df['H-PC'] = abs(df['High'] - df['Close'].shift(1))
    df['L-PC'] = abs(df['Low'] - df['Close'].shift(1))
    tr = df[['H-L', 'H-PC', 'L-PC']].max(axis=1)
    return tr.rolling(period).mean()


def is_consolidating(df, days=10, threshold=0.03):
    recent = df.tail(days)
    max_close = recent['Close'].max()
    min_close = recent['Close'].min()
    return (max_close - min_close) / min_close < threshold


def is_liquid(df):
    return df['Volume'].iloc[-1] > MIN_VOLUME


# =========================
# MAIN ENGINE
# =========================

def run_btst(capital=10000):

    print("\n========== BTST AI ENGINE ==========\n")

    # Market Regime Check
    if market_regime() != "BULLISH":
        print("Market not bullish. Skipping BTST today.")
        return None

    print("Market Regime: BULLISH\n")

    # Example Nifty 200 universe (replace with dynamic loader later)
    symbols = [
        "RELIANCE.NS", "HDFCBANK.NS", "INFY.NS",
        "ICICIBANK.NS", "LT.NS", "TCS.NS"
    ]

    best_pick = None
    best_score = 0

    for symbol in symbols:
        try:
            df = yf.download(symbol, period="3mo", interval="1d", progress=False)

            if len(df) < 50:
                continue

            # Indicators
            df['RSI'] = calculate_rsi(df, RSI_PERIOD)
            df['ATR'] = calculate_atr(df, ATR_PERIOD)

            latest = df.iloc[-1]

            # Filters
            if not is_liquid(df):
                continue

            if latest['RSI'] < 55:
                continue

            if not is_consolidating(df, CONSOLIDATION_DAYS):
                continue

            # Score logic
            score = latest['RSI']

            if score > best_score:
                best_score = score
                best_pick = (symbol, latest)

        except Exception as e:
            print(f"Error processing {symbol}: {e}")
            continue

    if not best_pick:
        print("No suitable BTST candidate found.")
        return None

    symbol, latest = best_pick

    entry_price = latest['Close']
    atr = latest['ATR']

    sl = entry_price - atr
    target = entry_price + (atr * RR_RATIO)

    quantity = calculate_position_size(
        capital=capital,
        risk_percent=RISK_PER_TRADE,
        entry=entry_price,
        stop_loss=sl
    )

    # =========================
    # LOG OUTPUT (IMPORTANT)
    # =========================

    print("✅ BTST Candidate Selected\n")
    print(f"Selected: {symbol}")
    print(f"Entry: ₹{round(entry_price,2)}")
    print(f"Stop Loss: ₹{round(sl,2)}")
    print(f"Target: ₹{round(target,2)}")
    print(f"ATR: ₹{round(atr,2)}")
    print(f"Position Size: {quantity} shares")
    print(f"Capital Used: ₹{round(quantity * entry_price,2)}")
    print("\n=====================================\n")

    return {
        "symbol": symbol,
        "entry": round(entry_price,2),
        "stop_loss": round(sl,2),
        "target": round(target,2),
        "quantity": quantity,
        "capital_used": round(quantity * entry_price,2),
        "date": datetime.now().strftime("%Y-%m-%d")
    }
