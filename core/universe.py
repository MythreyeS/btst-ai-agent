import requests
import pandas as pd


def get_nifty200_universe():
    """
    Dynamically fetch Nifty 200 list from NSE website.
    Fallback to static list if API fails.
    """

    try:
        print("Fetching Nifty 200 universe...")

        url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20200"

        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        }

        session = requests.Session()
        session.get("https://www.nseindia.com", headers=headers)
        response = session.get(url, headers=headers)

        data = response.json()

        symbols = []
        for item in data["data"]:
            symbols.append(item["symbol"] + ".NS")

        print(f"Loaded {len(symbols)} stocks from Nifty 200.")
        return symbols

    except Exception as e:
        print("Live fetch failed. Using fallback list.")
        print("Error:", e)

        # Fallback mini list
        return [
            "RELIANCE.NS",
            "HDFCBANK.NS",
            "ICICIBANK.NS",
            "TCS.NS",
            "INFY.NS",
            "TATAMOTORS.NS",
            "SBIN.NS",
            "AXISBANK.NS",
            "LT.NS",
            "BAJFINANCE.NS"
        ]
