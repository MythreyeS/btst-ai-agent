import pandas as pd
from core.indicators import is_consolidating

def consolidation_score(df: pd.DataFrame, days: int = 10) -> float:
    """
    1.0 if consolidating, else 0.0
    """
    if df is None or df.empty:
        return 0.0
    return 1.0 if is_consolidating(df, days=days, threshold=0.03) else 0.0
