from agents.regime_agent import market_regime
from agents.rsi_agent import rsi_signal
from agents.consolidation_agent import consolidation_signal

def run_btst_agents(universe):

    print("Running BTST AI Engine...")

    regime = market_regime()

    if regime != "BULLISH":
        print("Market not bullish. Skipping BTST.")
        return None

    scores = []

    for symbol in universe[:50]:  # limit for speed

        score = 0

        score += rsi_signal(symbol)
        score += consolidation_signal(symbol)

        if score >= 2:
            scores.append((symbol, score))

    if not scores:
        print("No strong BTST candidates.")
        return None

    scores.sort(key=lambda x: x[1], reverse=True)

    best_pick = scores[0][0]

    print(f"Selected Stock: {best_pick}")

    return best_pick
