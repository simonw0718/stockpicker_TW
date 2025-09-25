# minimal contract stub for tests
from typing import List, Dict

def evaluate_alerts(at_iso: str) -> List[Dict]:
    # 需提供 list，每筆至少包含 'symbol' 與 'status'
    return [{"symbol": "2330", "alert": "noop", "status": "ok"}]