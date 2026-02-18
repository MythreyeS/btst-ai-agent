from agents.regime_agent import market_regime
from agents.rsi_agent import rsi_signal
from agents.consolidation_agent import consolidation_signal
from agents.gap_agent import gap_probability
from agents.atr_agent import atr_levels
from capital_manager import get_capital, calculate_position_size

def run_btst_agents(universe):

    print("🚀 Running BTST AI Engine...")

    regime = market_regime()

    if regime != "BULLISH":
        print("Market not bullish.")
        return None

    capital = get_capital()
    risk_percent = 0.02

    print(f"Available Capital: ₹{capital}")
    print(f"Risk Per Trade: {risk_percent*100}%")

    candidates = []

    for symbol in universe[:80]:

        score = 0
        score += rsi_signal(symbol)
        score += consolidation_signal(symbol)
        score += gap_probability(symbol)

        if score >= 2:
            candidates.append(symbol)

    if not candidates:
        return None

    best = candidates[0]

    entry, stop, target = atr_levels(best)
    qty = calculate_position_size(capital, risk_percent, entry, stop)

    print(f"Selected: {best}")
    print(f"Entry: {entry}")
    print(f"Stop: {stop}")
    print(f"Target: {target}")
    print(f"Quantity: {qty}")

    return {
        "symbol": best,
        "entry": entry,
        "stop": stop,
        "target": target,
        "qty": qty
    }
