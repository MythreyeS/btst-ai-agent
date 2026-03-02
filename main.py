import yfinance as yf
from datetime import datetime
from agents.regime_agent import get_market_regime
from btst_orchestrator import run_btst_agents
from core.universe_manager import load_universe, get_sector
from telegram import send_telegram

CAPITAL = 100000


def _arrow(pct: float) -> str:
    if pct > 0.05:
        return "🟢⬆"
    if pct < -0.05:
        return "🔴⬇"
    return "⚪➡"


def main():
    try:
        # -------------------------------------------------
        # 1️⃣ Get Market Regime
        # -------------------------------------------------
        nifty = yf.download("^NSEI", period="30d", interval="1d", progress=False)
        nifty_close = float(nifty["Close"].iloc[-1])
        sma20 = float(nifty["Close"].rolling(20).mean().iloc[-1])

        regime = get_market_regime()

        if regime == "BEARISH":
            regime_note = "⚠ Bearish – Hunter Mode Active"
            allocation_multiplier = 0.5
        else:
            regime_note = "🚀 Bullish Momentum Active"
            allocation_multiplier = 1.0

        # -------------------------------------------------
        # 2️⃣ Load Universe
        # -------------------------------------------------
        symbols = load_universe()

        # -------------------------------------------------
        # 3️⃣ Run BTST Agents (No Regime Blocking)
        # -------------------------------------------------
        shortlisted = run_btst_agents(symbols)

        # -------------------------------------------------
        # 4️⃣ Format Message
        # -------------------------------------------------
        message = "📊 *BTST AI Advisor*\n\n"
        message += f"📈 Nifty Close: {nifty_close:.2f}\n"
        message += f"📉 SMA20: {sma20:.2f}\n"
        message += f"🧭 Regime: {regime}\n"
        message += f"{regime_note}\n\n"

        if not shortlisted:
            message += "❌ No strong setups detected today.\n"
            send_telegram(message)
            return

        message += "🔥 *Opportunity Hunter Picks*\n\n"

        for stock in shortlisted[:5]:
            symbol = stock["symbol"]
            score = stock.get("score", 0)
            entry = stock.get("entry", 0)
            target = stock.get("target", 0)
            stop = stock.get("stop", 0)

            sector = get_sector(symbol)

            risk = entry - stop if entry and stop else 0
            reward = target - entry if entry and target else 0

            rr = reward / risk if risk != 0 else 0

            allocation = (CAPITAL * allocation_multiplier) / 5

            message += (
                f"🏷 {symbol} ({sector})\n"
                f"Entry: {entry:.2f}\n"
                f"Target: {target:.2f}\n"
                f"Stop: {stop:.2f}\n"
                f"R:R: {rr:.2f}\n"
                f"Confidence: {score}%\n"
                f"Allocation: ₹{allocation:.0f}\n\n"
            )

        send_telegram(message)

    except Exception as e:
        send_telegram(f"❌ BTST Engine Error:\n{str(e)}")


if __name__ == "__main__":
    main()
