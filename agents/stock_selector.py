import yfinance as yf
from core.universe_manager import load_universe


def scan_top_movers():
    """
    Returns:
      movers: list[dict]
      sector_top: str
      man_of_match: dict
    movers dict format:
      {
        "symbol": "RELIANCE.NS",
        "sector": "Energy",
        "change_pct": 1.23,
        "prev_close": 2450.0,
        "close": 2480.0
      }
    """

    universe = load_universe()  # must return list of {"symbol":..., "sector":...}

    results = []

    # Keep it stable (yfinance rate limits if you do 500 at once)
    for stock in universe[:80]:
        # Strong validation: stock MUST be a dict
        if not isinstance(stock, dict):
            continue

        symbol = stock.get("symbol")
        sector = stock.get("sector", "Unknown")

        if not symbol:
            continue

        try:
            df = yf.download(symbol, period="2d", interval="1d", progress=False)

            if df is None or len(df) < 2:
                continue

            prev_close = float(df["Close"].iloc[-2])
            close = float(df["Close"].iloc[-1])

            if prev_close == 0:
                continue

            change_pct = ((close - prev_close) / prev_close) * 100.0

            results.append({
                "symbol": symbol,
                "sector": sector,
                "change_pct": round(change_pct, 2),
                "prev_close": round(prev_close, 2),
                "close": round(close, 2),
            })

        except Exception:
            continue

    if not results:
        return [], "N/A", {}

    results.sort(key=lambda x: x["change_pct"], reverse=True)

    movers = results[:5]
    man_of_match = movers[0]

    # Sector leader based on top-5 dominance
    sector_counts = {}
    for r in movers:
        sec = r.get("sector", "Unknown")
        sector_counts[sec] = sector_counts.get(sec, 0) + 1

    sector_top = max(sector_counts, key=sector_counts.get) if sector_counts else "N/A"

    return movers, sector_top, man_of_match
