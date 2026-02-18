import yfinance as yf

def gap_probability(symbol):
    data = yf.download(symbol, period="6mo", interval="1d", progress=False)

    data["gap"] = (data["Open"] - data["Close"].shift()) / data["Close"].shift()

    positive_gaps = data[data["gap"] > 0.005]

    if len(data) == 0:
        return 0

    probability = len(positive_gaps) / len(data)

    if probability > 0.3:
        return 1
    return 0
