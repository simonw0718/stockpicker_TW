# src/app/runners/scan_runner.py
# minimal contract stub for tests
from typing import List, Dict

def run_scan(symbols: List[str]) -> List[Dict]:
    # 回傳每個 symbol 一筆結果；需包含 'symbol' 與 'signal_type'
    return [{"symbol": s, "signal_type": "noop", "status": "ok"} for s in symbols]