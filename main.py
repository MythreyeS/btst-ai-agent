import sys
from btst_orchestrator import run_btst_agents
from trade_manager import save_open_trade, close_trade_if_due, has_open_trade
from weekly_tracker import update_weekly_performance
from capital_manager import get_capital
from telegram import send_message
from backtest_engine import run_backtest

def _format_pick(p: dict) -> str:
    return (
        f"📌 BTST AI Pick ({p['date']})\n"
        f"✅ Symbol: {p['symbol']}\n"
        f"Entry: ₹{p['entry']} | SL: ₹{p['stop_loss']} | Target: ₹{p['target']}\n"
        f"Qty: {p['quantity']} | Capital Used: ₹{p['capital_used']}\n"
        f"Score: {p['final_score']}\n"
        f"Agent Scores: {p['scores']}\n"
        f"Votes: {p['votes']}"
    )

def _format_close(c: dict) -> str:
    return (
        f"📉 BTST Trade Closed\n"
        f"Symbol: {c['symbol']}\n"
        f"Entry({c['entry_date']}): ₹{c['entry']}  -> Exit({c['exit_date']}): ₹{c['exit']}\n"
        f"Qty: {c['qty']} | PnL: ₹{c['pnl']} ({c['pnl_pct']}%)\n"
        f"Exit Reason: {c['exit_reason']}\n"
        f"Capital Now: ₹{c['capital_after']}"
    )

def _weekly_alert_if_hit() -> None:
    # update weekly performance and alert if weekly pnl >= 20k (you asked for alert, not stop)
    res = update_weekly_performance()
    if res.get("status") != "updated":
        return
    latest = res.get("latest_week", {})
    pnl = float(latest.get("pnl", 0.0))
    week = str(latest.get("week", ""))
    if pnl >= 20000:
        send_message(f"🎯 Weekly Target Alert: {week}\n✅ Weekly PnL: ₹{round(pnl,2)} reached/exceeded ₹20,000.")

def main():
    mode = (sys.argv[1] if len(sys.argv) > 1 else "btst").lower()
    lookback = int(sys.argv[2]) if len(sys.argv) > 2 else 60

    if mode == "btst":
        # If a trade is still open, do not open another (you can change later)
        if has_open_trade():
            send_message("⚠️ BTST AI: Open trade exists. Run CLOSE mode first.")
            return

        pick = run_btst_agents()
        if pick.get("status") != "picked":
            send_message(f"BTST AI: No pick today. Reason: {pick.get('reason', pick.get('status'))}")
            return

        save_open_trade({
            "symbol": pick["symbol"],
            "entry_date": pick["date"],
            "entry": pick["entry"],
            "stop_loss": pick["stop_loss"],
            "target": pick["target"],
            "quantity": pick["quantity"],
        })

        send_message(_format_pick(pick))
        _weekly_alert_if_hit()

    elif mode == "close":
        closed = close_trade_if_due()
        if closed.get("status") == "closed":
            send_message(_format_close(closed))
            _weekly_alert_if_hit()
        else:
            send_message(f"BTST AI Close: {closed.get('status')}")

    elif mode == "backtest":
        res = run_backtest(lookback_days=lookback, start_capital=10000.0)
        msg = (
            f"🧪 Backtest Done ({lookback} days)\n"
            f"Trades: {res.get('trades')}\n"
            f"Start: ₹{res.get('start_capital')} | End: ₹{res.get('end_capital')}\n"
            f"Net PnL: ₹{res.get('net_pnl')}\n"
            f"CSV: {res.get('backtest_csv')}"
        )
        send_message(msg)

    else:
        print("Invalid mode. Use: btst / close / backtest")
        print("Example: python main.py btst")
        print("Example: python main.py close")
        print("Example: python main.py backtest 60")

if __name__ == "__main__":
    main()
