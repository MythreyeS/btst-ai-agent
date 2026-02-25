# btst_orchestrator.py

from market_regime import get_market_regime
from stock_scanner import scan_top_movers
from policy import get_policy
from telegram import send_btst_daily_report


def run_btst_agents():
    """
    Main BTST Orchestration Pipeline
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
