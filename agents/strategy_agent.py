from core.storage import load_json, save_json

POLICY_FILE = "data/policy.json"

DEFAULT_POLICY = {
    "weights": {
        "trend_50dma": 0.20,
        "breakout_20": 0.20,
        "vol_ratio": 0.20,
        "mom_1d": 0.15,
        "mom_5d": 0.10,
        "close_near_high": 0.10,
        "consolidating": 0.05
    },
    "threshold": 0.62,   # score threshold for trade eligibility
    "rsi_low": 50,
    "rsi_high": 70
}

def load_policy():
    policy = load_json(POLICY_FILE, DEFAULT_POLICY)
    if "weights" not in policy:
        policy = DEFAULT_POLICY
    return policy

def save_policy(policy):
    save_json(POLICY_FILE, policy)

def score_candidate(features: dict, policy: dict) -> float:
    """
    Strategy Agent: computes probability-like score using policy weights.
    """
    w = policy["weights"]
    # normalize vol_ratio into 0..1 (cap)
    vol_score = min(max(features["vol_ratio"] / 2.0, 0.0), 1.0)

    # momentum normalize (cap)
    mom1 = min(max(features["mom_1d"] / 0.03, 0.0), 1.0)   # 3% = 1.0
    mom5 = min(max(features["mom_5d"] / 0.06, 0.0), 1.0)   # 6% = 1.0

    score = 0.0
    score += w["trend_50dma"] * float(features["trend_50dma"])
    score += w["breakout_20"] * float(features["breakout_20"])
    score += w["vol_ratio"] * vol_score
    score += w["mom_1d"] * mom1
    score += w["mom_5d"] * mom5
    score += w["close_near_high"] * float(features["close_near_high"])
    score += w["consolidating"] * float(features["consolidating"])

    # hard filters inside strategy agent (not scanner)
    if features["liquid"] < 1.0:
        return 0.0
    if not (policy["rsi_low"] < features["rsi"] < policy["rsi_high"]):
        return 0.0
    if features["strong_close"] < 1.0:
        return 0.0

    return score

def pick_best(candidates: list[dict], policy: dict) -> dict | None:
    scored = []
    for f in candidates:
        s = score_candidate(f, policy)
        if s >= policy["threshold"]:
            scored.append((s, f))
    if not scored:
        return None
    scored.sort(key=lambda x: x[0], reverse=True)
    best_score, best_feat = scored[0]
    best_feat["agent_score"] = float(best_score)
    return best_feat
