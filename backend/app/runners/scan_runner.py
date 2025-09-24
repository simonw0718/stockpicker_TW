# backend/app/runners/scan_runner.py
from typing import List, Dict
from datetime import datetime, UTC

def run_scan(universe: List[str], timeframe: str = "1D") -> List[Dict]:
    """
    Phase0 stub: 批次掃描器
    回傳假 signals
    """
    now = datetime.now(UTC).isoformat()
    return [{
        "symbol": s,
        "timeframe": timeframe,
        "signal_type": "bullish",
        "strength": 50,
        "ts": now,
        "meta": "{}"
    } for s in universe]