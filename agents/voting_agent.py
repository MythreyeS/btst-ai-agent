from typing import Dict, Tuple
import numpy as np

DEFAULT_WEIGHTS = {
    "rsi": 0.30,
    "consolidation": 0.20,
    "gap": 0.25,
    "liquidity": 0.25
}

def combine_scores(scores: Dict[str, float], weights: Dict[str, float]) -> Tuple[float, Dict[str, int]]:
    """
    Returns:
      final_score 0..1
      votes dict (agent -> 0/1)
    """
    # votes = score >= 0.5
    votes = {k: (1 if float(v) >= 0.5 else 0) for k, v in scores.items()}

    # weighted average
    total_w = sum(weights.get(k, 0.0) for k in scores.keys())
    if total_w <= 0:
        return 0.0, votes

    final = 0.0
    for k, v in scores.items():
        final += float(v) * float(weights.get(k, 0.0))

    final = final / total_w
    return float(np.clip(final, 0.0, 1.0)), votes
