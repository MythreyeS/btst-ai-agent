from agents.regime_agent import get_market_regime
from telegram import send_telegram
from btst_orchestrator import run_btst_agents


def main():

    print("🚀 Running BTST AI Engine...")

    regime, close, sma20 = get_market_regime()

    print(f"Nifty Close: {close}")
    print(f"Nifty SMA20: {sma20}")
    print(f"Market Regime: {regime}")

    capital = 100000  # Example capital

    if regime == "BEARISH":

        message = f"""
📊 BTST AI Engine – Daily Report

Index: NIFTY 50
Close: {close:.2f}
SMA20: {sma20:.2f}
Regime: 🔴 BEARISH

Decision: ❌ No Trade
Capital Protected.
"""
        send_telegram(message)
        return

    elif regime == "NEUTRAL":
        capital = capital * 0.5

    # If BULLISH → full capital
    selected_stocks = run_btst_agents()

    if not selected_stocks:
        message = f"""
📊 BTST AI Engine – Daily Report

Index: NIFTY 50
Close: {close:.2f}
SMA20: {sma20:.2f}
Regime: {regime}

No valid BTST setups today.
"""
        send_telegram(message)
        return

    # Format trade message
    stock_list = "\n".join([f"• {stock}" for stock in selected_stocks])

    message = f"""
📊 BTST AI Engine – Trade Alert

Index: NIFTY 50
Close: {close:.2f}
SMA20: {sma20:.2f}
Regime: {regime}

Allocated Capital: ₹{int(capital)}

🎯 Selected Stocks:
{stock_list}
"""

    send_telegram(message)


if __name__ == "__main__":
    main()
