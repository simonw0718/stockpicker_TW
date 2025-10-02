# src/app/routers/scan.py
from fastapi import APIRouter, Header, HTTPException
from typing import Optional, Dict, Any, List
from datetime import datetime
from ..repositories.signals import SignalsRepo
from ..repositories.alerts import AlertsRepo
from ..db.conn import get_conn
from app.config import get_env_int

router = APIRouter(prefix="/api/v1/scan", tags=["scan"])
signals_repo = SignalsRepo()
alerts_repo = AlertsRepo()

@router.post("")
def submit_scan(
    payload: Dict[str, Any],
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
):
    if not idempotency_key:
        raise HTTPException(
            status_code=400,
            detail={"error_code": "VALIDATION_ERROR", "message": "Idempotency-Key required"},
        )
    db = None
    job_id = signals_repo.get_or_create_scan_job(db, idempotency_key)
    return {"job_id": job_id, "status": "pending"}

@router.get("")
def noop_for_now():
    return {"status": "not_implemented"}

# --------- 立即執行的 stub runner（方便 e2e 測試） ---------
@router.post("/run-now")
def run_now(
    payload: Dict[str, Any],
    x_symbols_limit: Optional[int] = Header(None, alias="X-Scan-Symbols-Limit"),
):
    """
    最小可用 stub：
      body:
        {
          "strategy_id": 1,
          "symbols": ["2330","2317"],
          "timeframe": "1D",
          "ts": "2025-09-28 00:00:00",
          "signal_type": "buy",
          "strength": 0.8,
          "auto_alert": true
        }
    回傳：{"inserted_signals": n, "created_alerts": m, "status": "ok"}
    """
    # ---- 參數基本檢核
    if "strategy_id" not in payload:
        raise HTTPException(status_code=422, detail={"error": "strategy_id required"})
    if "symbols" not in payload or not isinstance(payload["symbols"], list) or len(payload["symbols"]) == 0:
        raise HTTPException(status_code=422, detail={"error": "symbols must be a non-empty array"})

    # symbols 上限（優先用每請求 header，其次環境變數，預設 500）
    try:
        per_request_limit = int(x_symbols_limit) if x_symbols_limit is not None else None
    except Exception:
        per_request_limit = None
    max_symbols = per_request_limit if per_request_limit is not None else get_env_int("SCAN_SYMBOLS_MAX", 500)
    if len(payload["symbols"]) > max_symbols:
        raise HTTPException(
            status_code=413,
            detail={
                "error_code": "PAYLOAD_TOO_LARGE",
                "message": f"symbols exceeds limit {max_symbols}",
                "limit": max_symbols,
                "got": len(payload["symbols"]),
            },
        )

    strategy_id: int = int(payload["strategy_id"])
    symbols: List[str] = [str(s) for s in payload["symbols"]]
    timeframe: str = str(payload.get("timeframe", "1D"))
    signal_type: str = str(payload.get("signal_type", "buy"))
    try:
        strength: float = float(payload.get("strength", 0.8))
    except Exception:
        strength = 0.8

    # ts 決定順序：ts > end_date > start_date > 今天 00:00:00
    ts = payload.get("ts") or payload.get("end_date") or payload.get("start_date")
    if not ts:
        ts = datetime.now().strftime("%Y-%m-%d 00:00:00")

    auto_alert: bool = bool(payload.get("auto_alert", False))

    # ---- 執行
    db = get_conn()
    inserted = 0
    created_alerts = 0
    for sym in symbols:
        # upsert signal
        sid = signals_repo.upsert_signal(
            db,
            {
                "strategy_id": strategy_id,
                "symbol": sym,
                "ts": ts,
                "timeframe": timeframe,
                "signal_type": signal_type,
                "strength": strength,
                "meta": {"runner": "stub_run_now"},
            },
        )
        inserted += 1 if sid else 0

        # optional：同步產生 alert（pending）
        if auto_alert:
            conn = db
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO alerts(symbol, condition, timeframe, status, last_triggered_ts, channel, created_at, updated_at)
                VALUES(?, ?, ?, 'pending', ?, 'webhook', datetime('now'), datetime('now'))
                """,
                (
                    sym,
                    f"strategy:{strategy_id}:{signal_type}",
                    timeframe,
                    ts,
                ),
            )
            conn.commit()
            created_alerts += 1

    return {"inserted_signals": inserted, "created_alerts": created_alerts, "status": "ok"}

@router.get("/{job_id}")
def get_scan_job(job_id: str):
    db = None
    rec = signals_repo.get_scan_job(db, job_id)
    if not rec:
        raise HTTPException(status_code=404, detail={"error": "NOT_FOUND", "message": "job not found"})
    return rec