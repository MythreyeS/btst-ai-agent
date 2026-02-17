import pandas as pd

NSE_NIFTY200_CSV = "https://archives.nseindia.com/content/indices/ind_nifty200list.csv"

FALLBACK = [
    "RELIANCE","TCS","INFY","HDFCBANK","ICICIBANK","SBIN","LT","ITC","AXISBANK","KOTAKBANK",
    "BHARTIARTL","HINDUNILVR","BAJFINANCE","HCLTECH","MARUTI","SUNPHARMA","TITAN","ULTRACEMCO"
]

def get_nifty200_symbols() -> list[str]:
    try:
        df = pd.read_csv(NSE_NIFTY200_CSV)
        if "Symbol" not in df.columns:
            return FALLBACK
        syms = df["Symbol"].dropna().astype(str).str.strip().tolist()
        syms = [s for s in syms if s and s.isupper()]
        return syms if syms else FALLBACK
    except Exception:
        return FALLBACK
