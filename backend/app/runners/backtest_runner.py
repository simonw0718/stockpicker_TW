# backend/app/runners/backtest_runner.py
from datetime import datetime, UTC
from typing import Dict, List, Tuple

def run_backtest(strategy: str, params: Dict, universe: List[str], date_range: Tuple[str, str]) -> Dict:
    """
    Phase0 stub: 回測器
    回傳假 run_id 與 metrics
    """
    ts = datetime.now(UTC).isoformat()
    return {
        "run_id": 1,
        "status": "done",
        "metrics": {"CAGR": 0.1, "Sharpe": 1.2},
        "created_at": ts,
        "finished_at": ts,
    }