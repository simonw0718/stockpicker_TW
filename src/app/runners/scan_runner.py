# src/app/runners/scan_runner.py
from __future__ import annotations
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import pandas as pd
import numpy as np

from app.indicators import registry as ind_registry

@dataclass
class ScanConfig:
    indicator: str = "ma"
    timeframe: str = "1D"
    params: Optional[Dict[str, Any]] = None  # e.g. {"window": 3}

def _make_minimal_ohlcv(n: int = 100) -> pd.DataFrame:
    """產生最小可用的 OHLCV DataFrame（單調遞增 close，方便產生 buy/sell 訊號）"""
    close = np.linspace(100, 110, num=n, dtype=float)
    high = close + 0.5
    low = close - 0.5
    open_ = close - 0.1
    volume = np.linspace(1000, 2000, num=n, dtype=float)
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": volume}
    )

def _validate_ohlcv(df: pd.DataFrame, need_rows: int) -> None:
    """基本防呆：欄位齊全且筆數足夠"""
    required = ["open", "high", "low", "close", "volume"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(f"missing columns: {missing}")
    if len(df) < need_rows:
        raise ValueError(f"need at least {need_rows} rows, got {len(df)}")

def _signal_from_indicator(close_last: float, indi_last: float) -> Dict[str, Any]:
    """
    最小策略：
      - close > indi → buy
      - close < indi → sell
      - 否則 noop
    strength = |close - indi| / max(1, |indi|) ，截斷 [0,1]
    """
    if indi_last is None or np.isnan(indi_last):
        return {"signal_type": "noop", "strength": 0.0}
    delta = float(close_last - indi_last)
    base = max(1.0, abs(indi_last))
    strength = max(0.0, min(1.0, abs(delta) / base))
    stype = "buy" if delta > 0 else ("sell" if delta < 0 else "noop")
    return {"signal_type": stype, "strength": strength}

def run_scan(
    symbols: List[str],
    *,
    indicator: str = "ma",
    timeframe: str = "1D",
    params: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    """
    回傳每個 symbol 一筆：
      {
        "symbol": "2330",
        "signal_type": "buy|sell|noop",
        "strength": 0.0~1.0,
        "meta": {"indicator": "...", "timeframe": "...", "params": {...}}
      }
    """
    if not symbols:
        return []

    # 預設參數：確保 ma/ema 至少有 window，避免 KeyError
    cfg_params: Dict[str, Any] = {"window": 5}
    cfg_params.update(params or {})

    # 資料與 warmup
    win = int(cfg_params.get("window", 5))
    n = max(5 * win, 50)  # 足夠 warmup
    df = _make_minimal_ohlcv(n=n)
    _validate_ohlcv(df, need_rows=n)

    # 計算指標（使用指標註冊表）
    indi_series = ind_registry.calc(indicator, df, cfg_params, timeframe=timeframe, field=None)
    indi_last = float(indi_series.iloc[-1]) if not pd.isna(indi_series.iloc[-1]) else np.nan
    close_last = float(df["close"].iloc[-1])
    sig = _signal_from_indicator(close_last, indi_last)

    # 對每個 symbol 輸出相同決策（runner 只計一次）
    out: List[Dict[str, Any]] = []
    for s in symbols:
        out.append(
            {
                "symbol": s,
                "signal_type": sig["signal_type"],
                "strength": sig["strength"],
                "meta": {
                    "indicator": indicator,
                    "timeframe": timeframe,
                    "params": cfg_params,
                },
            }
        )
    return out