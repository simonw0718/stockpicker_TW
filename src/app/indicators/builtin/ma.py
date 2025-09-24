import pandas as pd

def compute(data: pd.DataFrame, params: dict, *, timeframe: str="1d", field=None) -> pd.Series:
    w = int(params["window"])
    s = data["close"].rolling(window=w, min_periods=w).mean()
    # 前 w-1 筆強制 NaN
    s.iloc[:w-1] = pd.NA
    return s
