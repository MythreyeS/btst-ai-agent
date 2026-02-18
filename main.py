import sys
from core.universe import get_nifty200_universe
from btst_orchestrator import run_btst_agents
from telegram import send_message

def main():

    mode = sys.argv[1]

    if mode == "btst":

        universe = get_nifty200_universe()
        result = run_btst_agents(universe)

        if result:
            msg = f"""
🔥 BTST SIGNAL
Stock: {result['symbol']}
Entry: {result['entry']}
Stop: {result['stop']}
Target: {result['target']}
Qty: {result['qty']}
"""
            print(msg)
            send_message(msg)

        else:
            print("No trade today.")

if __name__ == "__main__":
    main()
