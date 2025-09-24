from typing import Dict, Any, Optional, Callable, List
import pandas as pd

RegistryType = Dict[str, Dict[str, Any]]  # name -> {"fn": callable, "meta": dict}
_REGISTRY: RegistryType = {}

def register(name: str, fn: Callable, meta: Dict[str, Any]) -> None:
    _REGISTRY[name] = {"fn": fn, "meta": meta}

def get(name: str) -> Dict[str, Any]:
    if name not in _REGISTRY:
        raise KeyError(f"indicator not registered: {name}")
    return _REGISTRY[name]

def calc(name: str, data: pd.DataFrame, params: Dict[str, Any], *, timeframe: str="1d", field: Optional[str]=None) -> pd.Series:
    entry = get(name)
    fn = entry["fn"]
    meta = entry.get("meta", {})
    # timeframe
    tfs: List[str] = meta.get("timeframes", ["1d"])
    if timeframe not in tfs:
        raise ValueError(f"timeframe not supported for {name}: {timeframe}")
    # columns check
    required = ["open","high","low","close","volume"]
    missing = [c for c in required if c not in data.columns]
    if missing:
        raise KeyError(f"missing columns: {missing}")

    out = fn(data, params, timeframe=timeframe, field=field)
    if hasattr(out, "columns"):  # DataFrame (multi-field)
        fields: Optional[List[str]] = meta.get("fields")
        default_field: Optional[str] = meta.get("default_field")
        chosen = field or default_field or (fields[0] if fields else None)
        if chosen is None or chosen not in out.columns:
            raise ValueError(f"field not available for {name}: {chosen}")
        return out[chosen]
    return out  # Series
