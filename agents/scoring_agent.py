import numpy as np


def score_stocks(candidate_stocks):

    scored = []

    for stock in candidate_stocks:

        price = stock["current_price"]
        volatility = stock["volatility"]

        # Simple AI signals (you can expand later)
        rsi_signal = 1 if volatility < 0.03 else 0
        liquidity_signal = 1
        consolidation_signal = 1 if volatility < 0.02 else 0
        gap_signal = 1

        votes = {
            "rsi": rsi_signal,
            "liquidity": liquidity_signal,
            "consolidation": consolidation_signal,
            "gap": gap_signal
        }

        agent_score = np.mean(list(votes.values())) * 100

        final_score = round(agent_score, 2)

        stock.update({
            "votes": votes,
            "final_score": final_score
        })

        # Filter threshold
        if final_score >= 50:
            scored.append(stock)

    # Sort by best score
    scored = sorted(scored, key=lambda x: x["final_score"], reverse=True)

    return scored[:3]   # Top 3 only
