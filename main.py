import yfinance as yf
from agents.regime_agent import get_market_regime
from btst_orchestrator import run_btst_agents
from telegram import send_telegram

CAPITAL = 100000


def main():
    try:
        # -------------------------------------------------
        # 1️⃣ Get Nifty Data
        # -------------------------------------------------
        nifty = yf.download("^NSEI", period="30d", interval="1d", progress=False)

        nifty_close = float(nifty["Close"].iloc[-1])
        sma20 = float(nifty["Close"].rolling(20).mean().iloc[-1])

        regime = get_market_regime()

        # -------------------------------------------------
        # 2️⃣ Hunter Mode (No Blocking)
        # -------------------------------------------------
        if regime == "BEARISH":
            regime_note = "⚠ Bearish – Hunter Mode Active"
            allocation_multiplier = 0.5
        else:
            regime_note = "🚀 Bullish Momentum Active"
            allocation_multiplier = 1.0

        # -------------------------------------------------
        # 3️⃣ Run BTST Agents (NO arguments)
        # -------------------------------------------------
        shortlisted = run_btst_agents()

        # -------------------------------------------------
        # 4️⃣ Build Telegram Message
        # -------------------------------------------------
        message = "📊 BTST AI Advisor\n\n"
        message += f"Nifty Close: {nifty_close:.2f}\n"
        message += f"SMA20: {sma20:.2f}\n"
        message += f"Regime: {regime}\n"
        message += f"{regime_note}\n\n"

        if not shortlisted:
            message += "❌ No strong setups detected today."
            send_telegram(message)
            return

        message += "🔥 Opportunity Hunter Picks\n\n"

        per_stock_capital = (CAPITAL * allocation_multiplier) / 5

        for stock in shortlisted[:5]:
            symbol = stock.get("symbol", "N/A")
            entry = stock.get("entry", 0)
            target = stock.get("target", 0)
            stop = stock.get("stop", 0)
            score = stock.get("score", 0)

            risk = entry - stop if entry and stop else 0
            reward = target - entry if entry and target else 0
            rr = reward / risk if risk != 0 else 0

            message += (
                f"{symbol}\n"
                f"Entry: {entry:.2f}\n"
                f"Target: {target:.2f}\n"
                f"Stop: {stop:.2f}\n"
                f"R:R: {rr:.2f}\n"
                f"Confidence: {score}%\n"
                f"Allocation: ₹{per_stock_capital:.0f}\n\n"
            )

        send_telegram(message)

    except Exception as e:
        send_telegram(f"❌ BTST Engine Error:\n{str(e)}")


if __name__ == "__main__":
    main()
