import yfinance as yf
import pandas as pd
from datetime import datetime

from core.universe_manager import fetch_nifty200_dynamic
from core.indicators import atr

from agents.regime_agent import market_regime
from agents.rsi_agent import rsi_score
from agents.consolidation_agent import consolidation_score
from agents.gap_agent import gap_probability_score
from agents.liquidity_agent import liquidity_score
from agents.voting_agent import combine_scores, DEFAULT_WEIGHTS

from core.utils import load_json, save_json
from capital_manager import get_capital, position_size


POLICY_PATH = "data/policy.json"

def load_policy():
    return load_json(POLICY_PATH, {"weights": DEFAULT_WEIGHTS})

def save_policy(policy: dict):
    save_json(POLICY_PATH, policy)

def run_btst_agents(universe_limit: int = 120) -> dict:
    """
    Returns dict with best pick and full explanation.
    """
    print("\n========== BTST AI ENGINE ==========\n")

    # Regime filter
    regime = market_regime()
    print(f"Market Regime: {regime}")
    if regime != "BULLISH":
        return {"status": "skipped", "reason": f"regime={regime}"}

    policy = load_policy()
    weights = policy.get("weights", DEFAULT_WEIGHTS)

    symbols = fetch_nifty200_dynamic(cache_path="data/nifty200.csv")
    symbols = symbols[:universe_limit]

    best = None
    best_score = -1

    for symbol in symbols:
        try:
            df = yf.download(symbol, period="6mo", interval="1d", progress=False)
            if df is None or df.empty or len(df) < 80:
                continue

            # compute ATR for SL/Target later
            df = df.dropna().copy()
            df["ATR"] = atr(df, 14)

            # agent scores (0..1)
            scores = {
                "rsi": rsi_score(df),
                "consolidation": consolidation_score(df),
                "gap": gap_probability_score(df),
                "liquidity": liquidity_score(df),
            }

            final_score, votes = combine_scores(scores, weights)

            # Hard guardrails: must have liquidity + RSI at least partially
            if scores["liquidity"] <= 0.0:
                continue
            if scores["rsi"] <= 0.0:
                continue

            if final_score > best_score:
                latest = df.iloc[-1]
                best_score = final_score
                best = {
                    "symbol": symbol,
                    "final_score": round(final_score, 4),
                    "scores": {k: round(float(v), 4) for k, v in scores.items()},
                    "votes": votes,
                    "close": float(latest["Close"]),
                    "atr": float(latest["ATR"]) if pd.notna(latest["ATR"]) else None,
                    "date": datetime.now().strftime("%Y-%m-%d"),
                }

        except Exception as e:
            print(f"Error on {symbol}: {e}")
            continue

    if not best:
        return {"status": "no_pick"}

    # Build trade plan
    entry = best["close"]
    atr_val = best["atr"] or (entry * 0.02)  # fallback 2%
    stop_loss = entry - atr_val
    target = entry + (atr_val * 1.8)

    capital = get_capital(10000.0)
    qty = position_size(capital=capital, risk_pct=0.01, entry=entry, stop=stop_loss)

    best.update({
        "status": "picked",
        "entry": round(entry, 2),
        "stop_loss": round(stop_loss, 2),
        "target": round(target, 2),
        "quantity": int(qty),
        "capital_used": round(entry * qty, 2)
    })

    # LOGS (as you asked)
    print("\n✅ BTST Candidate Selected\n")
    print(f"Selected: {best['symbol']}")
    print(f"Entry: ₹{best['entry']}")
    print(f"Stop Loss: ₹{best['stop_loss']}")
    print(f"Target: ₹{best['target']}")
    print(f"Position Size: {best['quantity']} shares")
    print(f"Score: {best['final_score']} | Scores: {best['scores']} | Votes: {best['votes']}")
    print("\n=====================================\n")

    return best
