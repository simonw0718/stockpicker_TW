# src/app/routers/signals.py （覆蓋或至少覆蓋 /upsert 端點）
from fastapi import APIRouter, HTTPException
from typing import Optional, Dict, Any
from ..repositories.signals import SignalsRepo

router = APIRouter(prefix="/api/v1/signals", tags=["signals"])
repo = SignalsRepo()

@router.get("")
def list_signals(start_ts: Optional[str] = None, end_ts: Optional[str] = None,
                 symbol: Optional[str] = None, strategy_id: Optional[int] = None, source: Optional[str] = None,
                 order_by: str = "ts", order: str = "desc", limit: int = 50, offset: int = 0):
    db = None
    items, total = repo.list_signals(
        db,
        start_ts=start_ts, end_ts=end_ts,
        symbol=symbol, strategy_id=strategy_id, source=source,
        order_by=order_by, order=order, limit=limit, offset=offset
    )
    return {"items": items, "total": total, "limit": limit, "offset": offset}

@router.post("/upsert", status_code=201)
def upsert_signal(body: Dict[str, Any]):
    required = ["strategy_id", "symbol", "ts"]
    missing = [k for k in required if body.get(k) in (None, "")]
    if missing:
        raise HTTPException(status_code=422, detail={
            "status": 422,
            "errors": [{"path": k, "code": "missing_required", "message": "field required"} for k in missing]
        })
    body.setdefault("timeframe", "1D")
    db = None
    sid = repo.upsert_signal(db, body)
    return {"signal_id": sid}