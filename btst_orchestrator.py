import traceback
from datetime import datetime

from agents.regime_agent import get_market_regime
from agents.strategy_agent import load_policy, pick_best
from core.universe_manager import get_candidates   # adjust if different
from capital_manager import get_available_capital
from telegram import send_telegram


def format_trade_message(regime, close_price, sma20, pick):
    header = f"""📊 BTST AI Engine – Daily Report

Index: NIFTY 50
Close: {close_price}
SMA20: {sma20}
Regime: {regime}
"""

    if not pick:
        body = "\n❌ No Trade Today.\nCapital Protected."
        return header + body

    body = f"""
🔥 BTST Pick:

➡ {pick['symbol']}
Entry: {pick.get('entry', 'Market')}
Target: {pick.get('target', '-')}
Stop: {pick.get('stop', '-')}
Strategy Score: {round(pick.get('agent_score', 0), 3)}
"""

    return header + body


def main():
    try:
        print("🚀 Starting BTST Orchestrator")

        # 1️⃣ Get market regime
        regime_data = get_market_regime()
        regime = regime_data["regime"]
        close_price = regime_data["close"]
        sma20 = regime_data["sma20"]

        print("Market Regime:", regime)

        # Always send regime update
        if regime != "BULLISH":
            message = format_trade_message(regime, close_price, sma20, None)
            send_telegram(message)
            print("📤 Sent no-trade message")
            return

        # 2️⃣ Load policy
        policy = load_policy()

        # 3️⃣ Get candidate features from universe manager
        candidates = get_candidates()   # must return list of feature dicts
        print("Candidates count:", len(candidates))

        # 4️⃣ Pick best using strategy agent
        best_pick = pick_best(candidates, policy)

        print("Best Pick:", best_pick)

        message = format_trade_message(regime, close_price, sma20, best_pick)

        send_telegram(message)
        print("📤 Telegram message sent successfully")

    except Exception as e:
        print("❌ Error in BTST Orchestrator")
        print(traceback.format_exc())

        error_message = f"""
⚠️ BTST Engine Error
Time: {datetime.now()}
Error: {str(e)}
"""
        send_telegram(error_message)


if __name__ == "__main__":
    main()
