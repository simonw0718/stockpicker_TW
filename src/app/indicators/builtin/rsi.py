import pandas as pd
import numpy as np

def compute(data: pd.DataFrame, params: dict, *, timeframe: str="1d", field=None) -> pd.Series:
    p = int(params["period"])
    close = data["close"]
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    # Wilder's RMA
    avg_gain = gain.ewm(alpha=1/p, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/p, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    # 邊界：avg_loss=0 => RSI=100；avg_gain=0=>RSI=0；皆0 => 50
    rsi = rsi.fillna(50)
    rsi.iloc[:max(p,1)] = pd.NA  # warm-up 前 p 筆 NaN（含第一筆）
    return rsi
