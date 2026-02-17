import pandas as pd
import time
from typing import List

NIFTY200_WIKI_URL = "https://en.wikipedia.org/wiki/NIFTY_200"

def _normalize_symbol(s: str) -> str:
    s = str(s).strip().upper()
    if not s.endswith(".NS"):
        s = s + ".NS"
    return s

def fetch_nifty200_dynamic(cache_path: str = "data/nifty200.csv") -> List[str]:
    """
    Tries:
      1) Wikipedia table scrape (read_html)
      2) local cache file fallback (data/nifty200.csv)

    Returns list of Yahoo symbols like RELIANCE.NS
    """
    # 1) Wikipedia scrape
    try:
        tables = pd.read_html(NIFTY200_WIKI_URL)
        # Find a table that contains "Symbol" or "Ticker"
        candidate = None
        for t in tables:
            cols = [c.lower() for c in t.columns.astype(str).tolist()]
            if any("symbol" in c for c in cols) or any("ticker" in c for c in cols):
                candidate = t
                break

        if candidate is not None:
            # Try common column names
            col = None
            for c in candidate.columns:
                lc = str(c).lower()
                if "symbol" in lc or "ticker" in lc:
                    col = c
                    break
            if col is not None:
                syms = candidate[col].dropna().astype(str).tolist()
                syms = [_normalize_symbol(x) for x in syms if x.strip()]
                syms = sorted(list(set(syms)))
                if len(syms) > 50:
                    # write cache
                    pd.DataFrame({"symbol": syms}).to_csv(cache_path, index=False)
                    return syms
    except Exception:
        pass

    # 2) Fallback cache
    try:
        df = pd.read_csv(cache_path)
        if "symbol" in df.columns:
            syms = df["symbol"].dropna().astype(str).tolist()
            syms = [_normalize_symbol(x) for x in syms if x.strip()]
            syms = sorted(list(set(syms)))
            return syms
    except Exception:
        pass

    # last resort minimal set
    return ["RELIANCE.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS", "TCS.NS", "LT.NS"]
