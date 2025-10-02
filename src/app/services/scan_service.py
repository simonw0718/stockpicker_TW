# src/app/services/scan_service.py
from __future__ import annotations
from typing import Dict, Any, List, Optional
from app.db.conn import get_conn
from app.runners.scan_runner import run_scan

class ScanService:
    def __init__(self, signals_repo):
        self.signals = signals_repo

    def submit_job(self, db, payload: Dict[str, Any]) -> Dict[str, str]:
        # 真正的批次掃描由 scheduler/worker 處理；此處僅回 job_id
        import uuid
        return {"job_id": str(uuid.uuid4()), "status": "pending"}

    def run_now(
        self,
        *,
        strategy_id: int,
        symbols: List[str],
        ts: str,
        timeframe: str = "1D",
        indicator: str = "ma",
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        直接執行掃描（同步）：呼叫 scan_runner → 將結果 upsert 到 signals
        回傳：{"inserted_signals": n, "status": "ok"}
        """
        if not symbols:
            return {"inserted_signals": 0, "status": "ok"}

        res = run_scan(symbols, indicator=indicator, timeframe=timeframe, params=params or {})
        conn = get_conn()
        inserted = 0
        for r in res:
            self.signals.upsert_signal(
                conn,
                {
                    "strategy_id": strategy_id,
                    "symbol": r["symbol"],
                    "ts": ts,
                    "timeframe": timeframe,
                    "signal_type": r["signal_type"],
                    "strength": r.get("strength"),
                    "meta": r.get("meta"),
                },
            )
            inserted += 1
        return {"inserted_signals": inserted, "status": "ok"}