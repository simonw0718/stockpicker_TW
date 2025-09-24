import pandas as pd

def compute(data: pd.DataFrame, params: dict, *, timeframe: str="1d", field=None) -> pd.Series:
    w = int(params["window"])
    s = data["close"].ewm(span=w, adjust=False).mean()
    # warm-up：前 w-1 設為 NaN
    s.iloc[:max(w-1,0)] = pd.NA
    return s
