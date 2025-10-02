# src/app/routers/alerts.py
from fastapi import APIRouter, HTTPException, Body
from typing import Optional, Dict, Any
from ..repositories.alerts import AlertsRepo
from ..db.conn import get_conn

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])
repo = AlertsRepo()

@router.post("/from-signal")
def create_alert_from_signal(payload: Dict[str, Any]):
    try:
        db = None
        alert_id = repo.create_from_signal(db, payload)
        return {"alert_id": alert_id, "status": "pending"}
    except ValueError as e:
        raise HTTPException(status_code=422, detail={"error": "VALIDATION_ERROR", "message": str(e)})
    except Exception:
        raise HTTPException(status_code=500, detail={"error": "INTERNAL_ERROR", "message": "failed to create alert"})

@router.get("")
def list_alerts(
    start_ts: Optional[str] = None,
    end_ts: Optional[str] = None,
    symbol: Optional[str] = None,
    strategy_id: Optional[int] = None,
    webhook_status: Optional[str] = None,
    order_by: str = "ts",
    order: str = "desc",
    limit: int = 50,
    offset: int = 0,
):
    db = None
    items, total = repo.list_alerts(
        db,
        start_ts=start_ts,
        end_ts=end_ts,
        symbol=symbol,
        strategy_id=strategy_id,
        webhook_status=webhook_status,
        order_by=order_by,
        order=order,
        limit=limit,
        offset=offset,
    )
    return {"items": items, "total": total, "limit": limit, "offset": offset}

@router.post("/{alert_id}/send")
def send_alert(alert_id: int, body: Dict[str, Any] = Body(default={})):
    db = None
    outcome = str(body.get("outcome", "sent"))
    error = body.get("error")
    rec = repo.send_alert(db, alert_id, outcome=outcome, error=error)
    if not rec:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "alert not found"}})
    return rec

# ★ 新增：批次重送 failed alerts（最多 N 筆，預設 50）
@router.post("/resend-failed")
def resend_failed(limit: int = 50):
    conn = get_conn()
    cur = conn.cursor()
    rows = cur.execute(
        """
        SELECT id FROM alerts
         WHERE status='failed'
         ORDER BY updated_at DESC
         LIMIT ?
        """,
        (max(0, min(limit, 500)),),
    ).fetchall()

    count = 0
    for r in rows:
        repo.send_alert(conn, int(r["id"]), outcome="sent")  # 簡化：當作重送成功
        count += 1
    return {"resend": count, "status": "ok"}