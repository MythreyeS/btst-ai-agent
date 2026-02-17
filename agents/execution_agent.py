from telegram import send_message
from trade_manager import save_trade

def build_trade_plan(best: dict, risk_pct: float) -> dict:
    """
    Uses ATR for dynamic SL/Target.
    """
    entry = float(best["close"])
    atr = float(best["atr"])

    # ATR guards
    if atr <= 0:
        atr = entry * 0.01  # fallback 1%

    sl = entry - (1.0 * atr)        # 1 ATR stop
    target = entry + (1.8 * atr)    # 1.8 ATR target

    return {
        "symbol": best["symbol"],
        "entry": entry,
        "sl": sl,
        "target": target,
        "atr": atr,
        "agent_score": float(best.get("agent_score", 0.0)),
        "risk_pct": float(risk_pct),
        "qty": 0  # filled by orchestrator/risk agent
    }

def send_trade_alert(plan: dict, capital: float, qty: int, regime: str) -> None:
    msg = (
        f"🔥 BTST AI Agent Trade\n\n"
        f"Regime: {regime}\n"
        f"Stock: {plan['symbol']}\n"
        f"Agent Score: {plan['agent_score']:.2f}\n\n"
        f"Entry (Close): ₹{plan['entry']:.2f}\n"
        f"SL (ATR): ₹{plan['sl']:.2f}\n"
        f"Target (ATR): ₹{plan['target']:.2f}\n"
        f"ATR: ₹{plan['atr']:.2f}\n\n"
        f"Capital: ₹{capital:,.0f}\n"
        f"Risk%: {plan['risk_pct']*100:.2f}%\n"
        f"Qty: {qty}\n\n"
        f"Note: Overnight gap risk exists."
    )
    send_message(msg)

def persist_open_trade(plan: dict) -> None:
    save_trade(plan)
