import yfinance as yf
import pandas as pd


def gap_probability(symbol):
    data = yf.download(symbol, period="6mo", interval="1d", progress=False)

    # If no data, return 0
    if data.empty:
        return 0

    # If multi-index columns (happens sometimes), flatten them
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)

    # Ensure required columns exist
    if "Open" not in data.columns or "Close" not in data.columns:
        return 0

    # Calculate gap safely
    data["gap"] = (data["Open"] - data["Close"].shift(1)) / data["Close"].shift(1)

    # Drop NaN rows (first row will be NaN)
    data = data.dropna()

    if len(data) == 0:
        return 0

    positive_gaps = data[data["gap"] > 0.005]

    probability = len(positive_gaps) / len(data)

    if probability > 0.3:
        return 1

    return 0
