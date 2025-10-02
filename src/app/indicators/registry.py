# src/app/indicators/registry.py
from typing import Dict, Any, Optional, Callable, List
import pandas as pd

RegistryType = Dict[str, Dict[str, Any]]  # key(lower) -> {"fn": callable, "meta": dict}
_REGISTRY: RegistryType = {}

def register(name: str, fn: Callable, meta: Dict[str, Any]) -> None:
    key = (name or "").lower()
    _REGISTRY[key] = {"fn": fn, "meta": meta or {}}

def get(name: str) -> Dict[str, Any]:
    key = (name or "").lower()
    if key not in _REGISTRY:
        raise KeyError(f"indicator not registered: {name}")
    return _REGISTRY[key]

def calc(
    name: str,
    data: pd.DataFrame,
    params: Dict[str, Any],
    *,
    timeframe: str = "1d",
    field: Optional[str] = None,
) -> pd.Series:
    entry = get(name)
    fn = entry["fn"]
    meta = entry.get("meta", {})

    # timeframe 正規化
    tf = (timeframe or "1d").lower()
    tfs: List[str] = [str(t).lower() for t in meta.get("timeframes", ["1d"])]
    if tf not in tfs:
        raise ValueError(f"timeframe not supported for {name}: {timeframe}")

    # 欄位檢查（OHLCV）
    required = ["open", "high", "low", "close", "volume"]
    missing = [c for c in required if c not in data.columns]
    if missing:
        raise KeyError(f"missing columns: {missing}")

    out = fn(data, params or {}, timeframe=tf, field=field)

    # multi-field 支援
    if hasattr(out, "columns"):
        fields: Optional[List[str]] = meta.get("fields")
        default_field: Optional[str] = meta.get("default_field")
        chosen = field or default_field or (fields[0] if fields else None)
        if chosen is None or chosen not in out.columns:
            raise ValueError(f"field not available for {name}: {chosen}")
        return out[chosen]

    return out