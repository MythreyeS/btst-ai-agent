import pandas as pd

NIFTY500_CSV_URL = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"


def load_universe():
    """
    Returns list of dicts:
    [
        {"symbol": "RELIANCE.NS", "sector": "Oil & Gas"},
        ...
    ]
    """

    try:
        df = pd.read_csv(NIFTY500_CSV_URL)
    except Exception:
        # If NSE fails temporarily, fallback to a safer minimal list
        return [
            {"symbol": "RELIANCE.NS", "sector": "Energy"},
            {"symbol": "HDFCBANK.NS", "sector": "Banking"},
            {"symbol": "INFY.NS", "sector": "IT"},
            {"symbol": "ICICIBANK.NS", "sector": "Banking"},
            {"symbol": "TCS.NS", "sector": "IT"},
        ]

    # NSE file usually contains: Symbol, Company Name, Industry, Series, ISIN Code
    symbol_col = "Symbol" if "Symbol" in df.columns else df.columns[0]
    sector_col = "Industry" if "Industry" in df.columns else None

    universe = []

    for _, row in df.iterrows():

        symbol = str(row[symbol_col]).strip()

        # Skip invalid rows
        if not symbol or symbol == "nan":
            continue

        sector = (
            str(row[sector_col]).strip()
            if sector_col and sector_col in row
            else "Unknown"
        )

        universe.append({
            "symbol": f"{symbol}.NS",
            "sector": sector
        })

    return universe

def scan_top_movers(*args, **kwargs):
    """
    Backward-compatible wrapper for orchestrator.
    This lets btst_orchestrator import scan_top_movers even if your
    internal function is named differently.
    """
    # ✅ If your actual function is named something else, map it here:
    if "select_top_movers" in globals():
        return select_top_movers(*args, **kwargs)

    if "get_top_movers" in globals():
        return get_top_movers(*args, **kwargs)

    if "run_stock_selector" in globals():
        return run_stock_selector(*args, **kwargs)

    # If none found, raise a clear error so we know the real function name
    raise ImportError(
        "scan_top_movers wrapper couldn't find select_top_movers / get_top_movers / run_stock_selector "
        "inside stock_selector.py. Please check the actual function name and map it here."
    )
