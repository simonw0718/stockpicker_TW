import pandas as pd

ALLOWED = {"open","high","low","close","volume"}

def compute(data: pd.DataFrame, params: dict, *, timeframe: str="1d", field=None) -> pd.Series:
    # 簡版：僅支援兩個基礎序列相減
    left = params.get("left"); right = params.get("right")
    if left not in ALLOWED or right not in ALLOWED:
        raise ValueError("DIFF.left/right must be one of open/high/low/close/volume")
    return data[left] - data[right]
