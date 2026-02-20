import traceback
from datetime import datetime

from agents.regime_agent import get_market_regime
from agents.strategy_agent import generate_btst_candidates
from agents.voting_agent import combine_scores, DEFAULT_WEIGHTS
from telegram import send_telegram


def run_btst_agents():

    candidates = generate_btst_candidates()

    final_picks = []

    for stock in candidates:

        # Expecting stock["agent_scores"] like:
        # {"rsi":0.7,"gap":0.6,"liquidity":0.8,"consolidation":0.5}
        scores = stock.get("agent_scores", {})

        if not scores:
            continue

        final_score, votes = combine_scores(scores, DEFAULT_WEIGHTS)

        if final_score >= 0.6:   # threshold
            stock["final_score"] = round(final_score * 100, 2)
            stock["votes"] = votes
            final_picks.append(stock)

    # sort highest conviction first
    final_picks.sort(key=lambda x: x["final_score"], reverse=True)

    return final_picks[:3]  # top 3


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

        selected_stocks = run_btst_agents()

        if not selected_stocks:
            send_telegram("No valid BTST setups today.")
            return

        body = ""
        for stock in selected_stocks:
            body += f"\n• {stock['symbol']}  | Conviction: {stock['final_score']}%\n"

        message = f"""
📊 BTST AI Engine – Trade Alert

Index: NIFTY 50
Close: {close:.2f}
SMA20: {sma20:.2f}
Regime: {regime}

🎯 Selected Stocks:
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
