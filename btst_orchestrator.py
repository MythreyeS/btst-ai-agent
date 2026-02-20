import traceback
from datetime import datetime

from agents.regime_agent import get_market_regime
from agents.strategy_agent import load_policy, pick_best
from core.universe_manager import fetch_nifty200_dynamic
from telegram import send_telegram


def run_btst_agents():

    symbols = fetch_nifty200_dynamic()

    # 🔥 TEMP: fake minimal feature set for now
    # (Replace later with real feature builder)
    candidates = []

    for sym in symbols[:20]:  # limit first 20 to avoid timeout
        features = {
            "symbol": sym,
            "trend_50dma": 1,
            "breakout_20": 1,
            "vol_ratio": 1.2,
            "mom_1d": 0.01,
            "mom_5d": 0.02,
            "close_near_high": 1,
            "consolidating": 0,
            "liquid": 1,
            "rsi": 60,
            "strong_close": 1
        }
        candidates.append(features)

    policy = load_policy()
    best = pick_best(candidates, policy)

    if not best:
        return []

    return [best]


def main():

    try:
        print("🚀 Running BTST AI Engine...")

        regime_data = get_market_regime()
        regime = regime_data["regime"]
        close = regime_data["close"]
        sma20 = regime_data["sma20"]

        if regime != "BULLISH":

            message = f"""
📊 BTST AI Engine – Daily Report

Index: NIFTY 50
Close: {close:.2f}
SMA20: {sma20:.2f}
Regime: {regime}

❌ No Trade Today.
Capital Protected.
"""
            send_telegram(message)
            return

        selected = run_btst_agents()

        if not selected:
            send_telegram("No valid BTST setups today.")
            return

        body = ""
        for stock in selected:
            body += f"\n• {stock['symbol']} | Score: {round(stock['agent_score']*100,2)}%"

        message = f"""
📊 BTST AI Engine – Trade Alert

Index: NIFTY 50
Close: {close:.2f}
SMA20: {sma20:.2f}
Regime: {regime}

🎯 Selected Stock:
{body}
"""

        send_telegram(message)

    except Exception as e:

        error_message = f"""
⚠️ BTST Engine Error
Time: {datetime.now()}
Error: {str(e)}
"""

        send_telegram(error_message)
        print(traceback.format_exc())


if __name__ == "__main__":
    main()
