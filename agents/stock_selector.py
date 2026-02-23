import pandas as pd


NIFTY500_CSV_URL = "https://archives.nseindia.com/content/indices/ind_nifty500list.csv"


def load_nifty500_universe():
    """
    Returns list of dicts:
      [{"symbol": "RELIANCE.NS", "sector": "Oil & Gas"}, ...]
    """
    try:
        df = pd.read_csv(NIFTY500_CSV_URL)
    except Exception:
        # Fallback minimal universe if NSE CSV temporarily fails
        fallback = [
            {"symbol": "RELIANCE.NS", "sector": "Unknown"},
            {"symbol": "HDFCBANK.NS", "sector": "Unknown"},
            {"symbol": "INFY.NS", "sector": "Unknown"},
            {"symbol": "ICICIBANK.NS", "sector": "Unknown"},
            {"symbol": "TCS.NS", "sector": "Unknown"},
        ]
        return fallback

    # NSE file usually has: Symbol, Company Name, Industry, Series, ISIN Code
    symbol_col = "Symbol" if "Symbol" in df.columns else df.columns[0]
    sector_col = "Industry" if "Industry" in df.columns else ("Sector" if "Sector" in df.columns else None)

    universe = []
    for _, row in df.iterrows():
        sym = str(row[symbol_col]).strip()
        if not sym or sym == "nan":
            continue
        sector = "Unknown"
        if sector_col and sector_col in df.columns:
            sector = str(row[sector_col]).strip()
            if not sector or sector == "nan":
                sector = "Unknown"

        universe.append({"symbol": f"{sym}.NS", "sector": sector})

    return universe
