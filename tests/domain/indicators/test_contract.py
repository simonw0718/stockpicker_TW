import pandas as pd
import numpy as np
import pytest

from app.indicators.registry import calc
import app.indicators  # side-effect: registers builtins

def mkdf(n=100, seed=0):
    rng = np.random.default_rng(seed)
    close = np.cumsum(rng.normal(0,1,size=n)) + 100
    high = close + rng.uniform(0,1,size=n)
    low = close - rng.uniform(0,1,size=n)
    open_ = close + rng.normal(0,0.5,size=n)
    volume = rng.integers(1000, 5000, size=n)
    idx = pd.date_range("2020-01-01", periods=n, freq="D")
    return pd.DataFrame({"open":open_,"high":high,"low":low,"close":close,"volume":volume}, index=idx)

def test_unregistered():
    df = mkdf()
    with pytest.raises(KeyError):
        calc("NOT_EXIST", df, {}, timeframe="1d")

def test_timeframe_guard():
    df = mkdf()
    with pytest.raises(ValueError):
        calc("RSI", df, {"period":14}, timeframe="1h")

def test_missing_columns():
    df = mkdf()[["close","volume"]]  # drop others
    with pytest.raises(KeyError):
        calc("MA", df, {"window":20})

def test_ma_warmup():
    df = mkdf()
    s = calc("MA", df, {"window":20})
    assert s.isna().sum() >= 19

def test_ema_ok():
    df = mkdf()
    s = calc("EMA", df, {"window":20})
    assert len(s) == len(df)

def test_rsi_ok():
    df = mkdf()
    s = calc("RSI", df, {"period":14})
    assert s.isna().sum() >= 14

def test_macd_field_and_default():
    df = mkdf()
    s_def = calc("MACD", df, {"fast":12,"slow":26,"signal":9})
    s_hist = calc("MACD", df, {"fast":12,"slow":26,"signal":9}, field="hist")
    assert len(s_def)==len(df) and len(s_hist)==len(df)

def test_boll_ok():
    df = mkdf()
    mid = calc("BOLL", df, {"window":20,"mult":2.0})  # default field=middle
    assert len(mid)==len(df)

def test_bias_ok():
    df = mkdf()
    s = calc("BIAS", df, {"window":20})
    assert len(s)==len(df)

def test_volume_raw_and_ma():
    df = mkdf()
    raw = calc("VOLUME", df, {})
    avg = calc("VOLUME", df, {"window":10})
    assert len(raw)==len(df) and len(avg)==len(df)

def test_diff_ok():
    df = mkdf()
    s = calc("DIFF", df, {"left":"close","right":"open"})
    assert len(s)==len(df)
