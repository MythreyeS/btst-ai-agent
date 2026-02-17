import sys
from telegram import send_message
from btst_orchestrator import run_btst_agents
from agents.review_agent import evaluate_open_trade
from agents.learning_agent import update_policy_from_recent

def main():
    if len(sys.argv) < 2:
        print("Mode required: test / btst / result / learn")
        return

    mode = sys.argv[1].lower().strip()

    if mode == "test":
        send_message("🚀 BTST Agent system is live!")

    elif mode == "btst":
        run_btst_agents()

    elif mode == "result":
        evaluate_open_trade()

    elif mode == "learn":
        update_policy_from_recent(window=20)
        send_message("🧠 Learning Agent: policy updated from recent trades (if enough data).")

    else:
        print("Invalid mode. Use: test / btst / result / learn")

if __name__ == "__main__":
    main()
