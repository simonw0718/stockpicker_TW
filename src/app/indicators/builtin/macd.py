import pandas as pd

def _ema(s: pd.Series, n: int) -> pd.Series:
    e = s.ewm(span=n, adjust=False).mean()
    e.iloc[:max(n-1,0)] = pd.NA
    return e

def compute(data: pd.DataFrame, params: dict, *, timeframe: str="1d", field=None) -> pd.DataFrame:
    fast = int(params["fast"]); slow = int(params["slow"]); signal = int(params["signal"])
    close = data["close"]
    ema_fast = _ema(close, fast)
    ema_slow = _ema(close, slow)
    macd = ema_fast - ema_slow
    signal_line = macd.ewm(span=signal, adjust=False).mean()
    signal_line.iloc[:max(signal-1,0)] = pd.NA
    hist = macd - signal_line
    return pd.DataFrame({"macd": macd, "signal": signal_line, "hist": hist})
