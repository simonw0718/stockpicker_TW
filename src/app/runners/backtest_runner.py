# minimal contract stub for tests
from typing import Dict, Any, List, Tuple
import uuid

def run_backtest(name: str, params: Dict[str, Any], symbols: List[str],
                 date_range: Tuple[str, str]) -> Dict[str, Any]:
    # 需包含 'run_id'、'metrics'、'status'
    return {
        "ok": True,
        "run_id": str(uuid.uuid4()),
        "status": "done",                   # 合約允許 'queued' 或 'done'
        "name": name,
        "symbols": symbols,
        "date_range": date_range,
        "metrics": {"sharpe": 0.0, "max_drawdown": 0.0},
    }