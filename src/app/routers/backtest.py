# src/app/routers/backtest.py
from fastapi import APIRouter, Header, HTTPException
from typing import Optional, Dict, Any
from ..repositories.backtests import BacktestsRepo
from ..repositories.trades import TradesRepo

router = APIRouter(prefix="/api/v1/backtest", tags=["backtest"])
backtests_repo = BacktestsRepo()
trades_repo = TradesRepo()

@router.post("")
def create_backtest(
    payload: Dict[str, Any],
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
):
    if not idempotency_key:
        raise HTTPException(
            status_code=400,
            detail={"error_code": "VALIDATION_ERROR", "message": "Idempotency-Key required"},
        )
    db = None
    return backtests_repo.create_run(db, payload, idempotency_key=idempotency_key)

@router.get("/{run_id}")
def get_backtest(run_id: int):
    db = None
    run = backtests_repo.get_run(db, run_id)
    if not run:
        raise HTTPException(
            status_code=404,
            detail={"error_code": "NOT_FOUND", "message": "run not found"},
        )
    return {
        "run": run,
        "links": {
            "trades": f"/api/v1/backtest/{run_id}/trades",
            "equity_curve": f"/api/v1/backtest/{run_id}/equity-curve",
        },
    }

@router.get("/{run_id}/trades")
def list_trades(
    run_id: int,
    limit: int = 50,
    offset: int = 0,
    order_by: str = "entry_ts",
    order: str = "asc",
):
    db = None
    items, total = trades_repo.list_by_run(
        db, run_id, order_by=order_by, order=order, limit=limit, offset=offset
    )
    return {"items": items, "total": total, "limit": limit, "offset": offset}

# ★ Demo / Stub：把 run 標記完成並自動塞一筆 trade（方便驗證前端流程）
@router.post("/{run_id}/complete")
def complete_backtest_stub(run_id: int):
    db = None
    run = backtests_repo.get_run(db, run_id)
    if not run:
        raise HTTPException(status_code=404, detail={"error_code": "NOT_FOUND", "message": "run not found"})
    backtests_repo.complete_run_stub(db, run_id)
    run2 = backtests_repo.get_run(db, run_id)
    return {"run": run2, "status": "completed_stub"}