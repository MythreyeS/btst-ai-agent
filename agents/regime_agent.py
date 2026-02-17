import yfinance as yf

def market_regime():

    df = yf.download("^NSEI", period="3mo", interval="1d", progress=False)

    df['SMA50'] = df['Close'].rolling(50).mean()
    df['SMA200'] = df['Close'].rolling(200).mean()

    latest = df.iloc[-1]

    if latest['SMA50'] > latest['SMA200']:
        return "BULLISH"
    else:
        return "BEARISH"
