import pandas as pd

def compute(data: pd.DataFrame, params: dict, *, timeframe: str="1d", field=None) -> pd.DataFrame:
    w = int(params["window"]); mult = float(params["mult"])
    m = data["close"].rolling(window=w, min_periods=w).mean()
    std = data["close"].rolling(window=w, min_periods=w).std(ddof=0)
    upper = m + mult*std
    lower = m - mult*std
    return pd.DataFrame({"upper": upper, "middle": m, "lower": lower})
