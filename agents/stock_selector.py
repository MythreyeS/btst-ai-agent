import yfinance as yf
from core.universe_manager import load_universe


def scan_top_movers():

    universe = load_universe()
    results = []

    for stock in universe[:50]:

        symbol = stock["symbol"]
        sector = stock["sector"]

        try:
            df = yf.download(symbol, period="2d", interval="1d", progress=False)

            if len(df) < 2:
                continue

            prev_close = float(df["Close"].iloc[-2])
            close = float(df["Close"].iloc[-1])

            change_pct = ((close - prev_close) / prev_close) * 100

            results.append({
                "symbol": symbol,
                "sector": sector,
                "change_pct": round(change_pct, 2),
                "prev_close": round(prev_close, 2),
                "close": round(close, 2),
            })

        except:
            continue

    if not results:
        return [], "N/A", {}

    results = sorted(results, key=lambda x: x["change_pct"], reverse=True)

    top5 = results[:5]

    man_of_match = top5[0]

    sectors = [x["sector"] for x in top5]
    sector_top = max(set(sectors), key=sectors.count)

    return top5, sector_top, man_of_match
