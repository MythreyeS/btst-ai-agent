from agents.market_regime import get_market_regime
from agents.stock_selector import load_nifty500_universe
from agents.scoring_agent import score_nifty500, RiskPolicy
from telegram import send_btst_daily_report


def main():
    market = get_market_regime()

    universe = load_nifty500_universe()

    policy = RiskPolicy(
        capital=50000.0,
        max_risk_pct_per_trade=0.02,
        stop_atr_mult=1.0,
        target_atr_mult=1.5
    )

    result = score_nifty500(universe=universe, market_regime=market, policy=policy)

    send_btst_daily_report(
        market_regime=market,
        policy={
            "capital": policy.capital,
            "max_risk_pct_per_trade": policy.max_risk_pct_per_trade
        },
        sector_top=result.get("sector_top"),
        man_of_match=result.get("man_of_match"),
        top5=result.get("top5", [])
    )


if __name__ == "__main__":
    main()
