from agents.strategy_agent import load_policy, pick_best
from agents.voting_agent import vote_on_stocks
from core.universe_manager import fetch_nifty200_dynamic
from agents.perception_agent import build_features   # adjust if name differs


def run_btst_agents():
    """
    Orchestrates all BTST agents and returns list of selected stock symbols.
    """

    # 1️⃣ Fetch Universe
    symbols = fetch_nifty200_dynamic()

    # 2️⃣ Build Feature Set
    features = build_features(symbols)   # Must return list[dict]

    if not features:
        return []

    # 3️⃣ Strategy Agent Scoring
    policy = load_policy()
    best_candidate = pick_best(features, policy)

    if not best_candidate:
        return []

    # 4️⃣ Voting Layer (optional)
    final_list = vote_on_stocks([best_candidate])

    if not final_list:
        return []

    # Return only symbols
    return [stock["symbol"] for stock in final_list]
