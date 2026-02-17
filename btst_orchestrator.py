from core.universe_manager import get_nifty200_symbols
from telegram import send_message

from agents.perception_agent import build_features
from agents.regime_agent import market_regime
from agents.strategy_agent import load_policy, pick_best
from agents.risk_agent import compute_risk_pct, position_size
from agents.execution_agent import build_trade_plan, send_trade_alert, persist_open_trade
from capital_manager import load_capital

def run_btst_agents():
    # Regime Agent
    reg = market_regime()
    if not reg["allow_btst"]:
        send_message(f"⚠️ Regime: {reg['regime']}. BTST not allowed today.")
        return

    # Universe
    symbols = get_nifty200_symbols()
    if not symbols:
        send_message("⚠️ Unable to load Nifty200 universe.")
        return

    # Perception Agent
    candidates = []
    for sym in symbols:
        f = build_features(sym)
        if f:
            candidates.append(f)

    if not candidates:
        send_message("No candidates passed Perception stage today.")
        return

    # Strategy Agent
    policy = load_policy()
    best = pick_best(candidates, policy)
    if not best:
        send_message("No candidate met strategy threshold today.")
        return

    # Risk Agent
    capital = load_capital(10000.0)
    risk_pct = compute_risk_pct(best["agent_score"], reg["risk_multiplier"])
    risk_amount = capital * risk_pct

    # Execution Agent (ATR SL/Target)
    plan = build_trade_plan(best, risk_pct)
    qty = position_size(plan["entry"], plan["sl"], risk_amount)
    plan["qty"] = qty

    # Persist open trade for next-day Review Agent
    persist_open_trade(plan)

    # Send alert
    send_trade_alert(plan, capital, qty, reg["regime"])
