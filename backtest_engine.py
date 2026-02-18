import yfinance as yf

def run_backtest(symbol):

    data = yf.download(symbol, period="6mo", interval="1d", progress=False)

    wins = 0
    losses = 0

    for i in range(50, len(data)-1):

        if data["Close"].iloc[i] > data["Close"].rolling(50).mean().iloc[i]:

            entry = data["Close"].iloc[i]
            next_day = data["Close"].iloc[i+1]

            if next_day > entry:
                wins += 1
            else:
                losses += 1

    total = wins + losses
    if total == 0:
        return 0

    winrate = wins / total
    print(f"Backtest Winrate: {winrate*100:.2f}%")

    return winrate
