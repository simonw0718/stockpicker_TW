import pandas as pd

def compute(data: pd.DataFrame, params: dict, *, timeframe: str="1d", field=None) -> pd.Series:
    w = int(params["window"])
    ma = data["close"].rolling(window=w, min_periods=w).mean()
    bias = (data["close"] - ma) / ma * 100
    return bias
