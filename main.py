import sys
from core.universe import get_nifty200_universe
from btst_orchestrator import run_btst_agents
from telegram import send_message

def main():

    if len(sys.argv) < 2:
        print("Usage: python main.py btst")
        return

    mode = sys.argv[1]

    if mode == "btst":

        print("Fetching Nifty 200 universe...")
        universe = get_nifty200_universe()

        pick = run_btst_agents(universe)

        if pick:
            message = f"🔥 BTST PICK: {pick}"
            print(message)
            send_message(message)
        else:
            print("No BTST pick today.")

    else:
        print("Invalid mode.")

if __name__ == "__main__":
    main()
