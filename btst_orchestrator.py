import pandas as pd
import yfinance as yf
from datetime import datetime

# Agent Imports
from agents.regime_agent import market_regime
from agents.rsi_agent import rsi_signal
from agents.gap_agent import gap_probability_score
from agents.consolidation_agent import consolidation_signal

# Core Imports
from capital_manager import get_capital, calculate_position_size
from trade_manager import save_open_trade
from telegram import send_message


def run_btst_agents(universe, risk_percent=2):
    """
    Main BTST AI Orchestrator
    """

    print("🚀 Running BTST AI Engine...")
    capital = get_capital()

    print(f"Available Capital: ₹{capital}")
    print(f"Risk Per Trade: {risk_percent}%")

    selected_trade = None
    highest_score = 0

    # ---- MARKET REGIME CHECK ----
    regime = market_regime()
    print(f"Market Regime: {regime}")

    if regime != "BULLISH":
        print("Market not bullish. No BTST trades today.")
        send_message("⚠ Market not bullish. No BTST trades today.")
        return

    # ---- SCAN UNIVERSE ----
    for symbol in universe:

        try:
            data = yf.download(symbol, period="3mo", interval="1d", progress=False)

            if len(data) < 50:
                continue

            close = data["Close"]
            latest_price = float(close.iloc[-1])

            # ---- AGENT SIGNALS ----
            rsi_score = rsi_signal(data)
            gap_score = gap_probability_score(data)
            consolidation_score = consolidation_signal(data)

            # Multi-Agent Voting System
            total_score = rsi_score + gap_score + consolidation_score

            print(f"{symbol} | RSI:{rsi_score} GAP:{gap_score} CONS:{consolidation_score} TOTAL:{total_score}")

            if total_score > highest_score:
                highest_score = total_score
                selected_trade = {
                    "symbol": symbol,
                    "entry": latest_price,
                    "score": total_score,
                    "data": data
                }

        except Exception as e:
            print(f"Error processing {symbol}: {e}")
            continue

    if not selected_trade:
        print("No high probability BTST trade found.")
        send_message("❌ No high probability BTST trade today.")
        return

    # ---- FINAL TRADE SELECTION ----
    symbol = selected_trade["symbol"]
    entry_price = selected_trade["entry"]
    data = selected_trade["data"]

    # ATR-based SL & Target
    atr = data["High"] - data["Low"]
    atr_value = atr.rolling(14).mean().iloc[-1]

    sl = entry_price - atr_value
    target = entry_price + (2 * atr_value)

    quantity = calculate_position_size(entry_price, risk_percent)

    print("\n🔥 FINAL BTST TRADE SELECTED 🔥")
    print(f"Selected: {symbol}")
    print(f"Entry: {entry_price}")
    print(f"Stop Loss: {sl}")
    print(f"Target: {target}")
    print(f"Position Size: {quantity}")
    print(f"Total Score: {highest_score}")

    # Save trade
    save_open_trade(
        symbol=symbol,
        entry=entry_price,
        stop_loss=sl,
        target=target,
        quantity=quantity
    )

    # Telegram Signal
    message = f"""
📈 BTST AI Signal

Stock: {symbol}
Entry: ₹{round(entry_price,2)}
Stop Loss: ₹{round(sl,2)}
Target: ₹{round(target,2)}
Quantity: {quantity}

Confidence Score: {highest_score}
"""

    send_message(message)

    print("✅ Signal Sent to Telegram")
