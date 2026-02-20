import traceback
from datetime import datetime

from agents.regime_agent import get_market_regime
from agents.strategy_agent import load_policy, pick_best
from agents.voting_agent import combine_scores, DEFAULT_WEIGHTS
from core.universe_manager import fetch_nifty200_dynamic
from telegram import send_telegram


# -------------------------------------------------
# Feature Builder (Minimal Stable Version)
# -------------------------------------------------

def build_features(symbol: str) -> dict:
    """
    Temporary deterministic feature builder.
    Replace later with real Yahoo feature extractor.
    """

    return {
        "symbol": symbol,
        "trend_50dma": 1,
        "breakout_20": 1,
        "vol_ratio": 1.2,
        "mom_1d": 0.01,
        "mom_5d": 0.02,
        "close_near_high": 1,
        "consolidating": 0,
        "liquid": 1,
        "rsi": 60,
        "strong_close": 1,
    }


# -------------------------------------------------
# Agent Pipeline
# -------------------------------------------------

def run_btst_agents():

    symbols = fetch_nifty200_dynamic()

    candidates = []
    policy = load_policy()

    for sym in symbols[:25]:  # limit for GitHub speed

        features = build_features(sym)

        strategy_score = pick_best([features], policy)

        if strategy_score is None:
            continue

        # Voting layer expects scores dict
        scores = {
            "rsi": 0.7,
            "consolidation": 0.6,
            "gap": 0.65,
            "liquidity": 0.8,
        }

        final_score, votes = combine_scores(scores, DEFAULT_WEIGHTS)

        if final_score >= 0.6:
            strategy_score["final_score"] = round(final_score * 100, 2)
            strategy_score["votes"] = votes
            candidates.append(strategy_score)

    candidates.sort(key=lambda x: x["final_score"], reverse=True)

    return candidates[:3]


# -------------------------------------------------
# Telegram Formatter
# -------------------------------------------------

def format_trade_message(regime, close, sma20, picks):

    header = f"""
📊 BTST AI Engine – Trade Alert

Index: NIFTY 50
Close: {close:.2f}
SMA20: {sma20:.2f}
Regime: {regime}
"""

    if not picks:
        return header + "\n\n❌ No Valid BTST Setups Today.\nCapital Protected."

    body = "\n\n🎯 Selected Stocks:\n"

    for stock in picks:
        body += f"""
• {stock['symbol']}
  Conviction: {stock['final_score']}%
  RSI: {stock['rsi']}
"""

    return header + body


# -------------------------------------------------
# MAIN
# -------------------------------------------------

def main():

    try:

        print("🚀 Running BTST AI Engine...")

        regime_data = get_market_regime()
        regime = regime_data["regime"]
        close = regime_data["close"]
        sma20 = regime_data["sma20"]

        if regime == "BEARISH":

            message = f"""
📊 BTST AI Engine – Daily Report

Index: NIFTY 50
Close: {close:.2f}
SMA20: {sma20:.2f}
Regime: 🔴 BEARISH

❌ No Trade Today.
Capital Protected.
"""
            send_telegram(message)
            return

        picks = run_btst_agents()

        message = format_trade_message(regime, close, sma20, picks)

        send_telegram(message)

        print("✅ Telegram Sent Successfully")

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
