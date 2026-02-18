import requests

def get_nifty200_universe():
    """
    Fetch Nifty 200 constituents from NSE official JSON.
    Returns list of Yahoo Finance symbols (with .NS)
    """

    url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20200"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://www.nseindia.com/"
    }

    session = requests.Session()
    session.headers.update(headers)

    try:
        response = session.get(url)
        data = response.json()

        symbols = []
        for stock in data["data"]:
            symbol = stock["symbol"] + ".NS"
            symbols.append(symbol)

        print(f"Loaded {len(symbols)} stocks from Nifty 200.")
        return symbols

    except Exception as e:
        print("Fallback to static list due to NSE block.")
        return [
            "RELIANCE.NS",
            "HDFCBANK.NS",
            "ICICIBANK.NS",
            "TCS.NS",
            "INFY.NS"
        ]
