import traceback
from datetime import datetime

from agents.regime_agent import get_market_regime
from agents.strategy_agent import generate_btst_candidates
from agents.voting_agent import vote_on_stocks
from capital_manager import get_available_capital
from telegram import send_telegram


def format_trade_message(regime, close_price, sma20, picks):
    header = f"""📊 BTST AI Engine – Daily Report

Index: NIFTY 50
Close: {close_price}
SMA20: {sma20}
Regime: {regime}
"""

    if not picks:
        body = "\n❌ No Trade Today.\nCapital Protected."
        return header + body

    body = "\n🔥 BTST Picks:\n"
    for stock in picks:
        body += f"""
➡ {stock['symbol']}
Entry: {stock['entry']}
Target: {stock['target']}
Stop: {stock['stop']}
Conviction: {stock['score']}/100
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

        # 2️⃣ If market not bullish → still send message
        if regime != "BULLISH":
            message = format_trade_message(regime, close_price, sma20, [])
            send_telegram(message)
            print("📤 Sent no-trade message")
            return

        # 3️⃣ Generate candidates
        candidates = generate_btst_candidates()
        print("Candidates:", candidates)

        # 4️⃣ Voting system
        final_picks = vote_on_stocks(candidates)
        print("Final Picks:", final_picks)

        # 5️⃣ Capital allocation logic
        capital = get_available_capital()
        print("Available Capital:", capital)

        message = format_trade_message(regime, close_price, sma20, final_picks)

        # 6️⃣ ALWAYS SEND TELEGRAM
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
