import pandas as pd

def compute(data: pd.DataFrame, params: dict, *, timeframe: str="1d", field=None) -> pd.Series:
    w = params.get("window")
    if w is None:
        return data["volume"]
    w = int(w)
    return data["volume"].rolling(window=w, min_periods=w).mean()
