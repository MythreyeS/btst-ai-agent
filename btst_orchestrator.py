# btst_orchestrator.py
from agents.market_regime import get_market_regime
from agents.stock_selector import scan_top_movers
from agents.capital_manager import get_policy
from telegram import send_btst_daily_report


def run_btst_agents():
    """
    Main BTST Orchestration Pipeline.
    Returns a list of dicts with keys:
        symbol, entry, target, stop, score
    """
    print("Running BTST Engine...")

    # 1️⃣ Market Regime
    market_regime = get_market_regime()

    # 2️⃣ Policy (Capital & Risk)
    policy = get_policy()

    # 3️⃣ Scan Movers
    movers, sector_top, man_of_match = scan_top_movers()

    # 4️⃣ Send Telegram Report
    send_btst_daily_report(
        market_regime=market_regime,
        policy=policy,
        sector_top=sector_top,
        man_of_match=man_of_match,
        movers=movers
    )

    print("BTST Report Sent Successfully.")

    # 5️⃣ Build shortlisted list expected by main.py
    shortlisted = []
    for stock in movers:
        close = stock.get("close", 0)
        change_pct = stock.get("change_pct", 0)

        # Calculate entry, target, stop from close price
        entry  = round(close, 2)
        target = round(close * 1.03, 2)   # 3% target
        stop   = round(close * 0.98, 2)   # 2% stop loss
        score  = min(int(abs(change_pct) * 10), 99)  # simple confidence proxy

        shortlisted.append({
            "symbol": stock.get("symbol", "N/A"),
            "entry":  entry,
            "target": target,
            "stop":   stop,
            "score":  score,
        })

    return shortlisted  # ✅ Returns list of dicts to main.py
