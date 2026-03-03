import yfinance as yf
import pandas as pd
from datetime import datetime
from core.universe_manager import load_universe


def scan_top_movers():
    """
    Scans the Nifty 200 universe and returns top movers by % change.

    Returns:
        top5       (list of dict)  - Top 5 gainers
        sector_top (str)           - Most represented sector in top 5
        man_of_match (dict)        - Highest % gainer
    """
    universe = load_universe()  # Now correctly returns list of dicts
    results = []

    for stock in universe[:100]:  # limit to 100 for stability
        symbol = stock["symbol"]
        sector = stock["sector"]

        try:
            df = yf.download(symbol, period="2d", interval="1d", progress=False)
            if len(df) < 2:
                continue

            prev_close = df["Close"].iloc[-2]
            close = df["Close"].iloc[-1]
            change_pct = ((close - prev_close) / prev_close) * 100

            results.append({
                "symbol": symbol,
                "sector": sector,
                "change_pct": round(float(change_pct), 2),
                "prev_close": round(float(prev_close), 2),
                "close": round(float(close), 2),
            })

        except Exception:
            continue

    if not results:
        return [], "N/A", {}

    # Sort by % change (descending)
    results = sorted(results, key=lambda x: x["change_pct"], reverse=True)
    top5 = results[:5]

    # Man of the Match = highest gainer
    man_of_match = top5[0]

    # Sector leader = most repeated sector in top 5
    sectors = [x["sector"] for x in top5]
    sector_top = max(set(sectors), key=sectors.count)

    return top5, sector_top, man_of_match
