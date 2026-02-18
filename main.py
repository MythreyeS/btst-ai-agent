import sys

from btst_orchestrator import run_btst_agents
from backtest_engine import run_backtest
from weekly_tracker import update_weekly_performance
from core.universe import get_nifty200_universe


def main():

    if len(sys.argv) < 2:
        print("Usage: python main.py btst | backtest")
        sys.exit(1)

    mode = sys.argv[1]

    # 🔥 Get Dynamic Nifty 200 Universe
    universe = get_nifty200_universe()

    if mode == "btst":
        print("Running BTST AI Engine...")
        pick = run_btst_agents(universe)

        if pick:
            print(f"\nFinal Pick: {pick}")
        else:
            print("No strong BTST candidate today.")

    elif mode == "backtest":
        print("Running Backtest Engine...")
        run_backtest(universe)

    elif mode == "weekly":
        update_weekly_performance()

    else:
        print("Invalid mode. Use btst | backtest | weekly")


if __name__ == "__main__":
    main()
