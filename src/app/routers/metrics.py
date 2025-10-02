# src/app/routers/metrics.py
from fastapi import APIRouter
from app.db.conn import get_conn

router = APIRouter(prefix="/api/v1/metrics", tags=["metrics"])

@router.get("")
def get_metrics():
    conn = get_conn()
    cur = conn.cursor()

    def one(sql: str, params: tuple = ()) -> int:
        return int(cur.execute(sql, params).fetchone()[0])

    return {
        "signals_total": one("SELECT COUNT(*) FROM signals"),
        "alerts_total": one("SELECT COUNT(*) FROM alerts"),
        "alerts_failed": one("SELECT COUNT(*) FROM alerts WHERE status='failed'"),
        "backtest_runs_total": one("SELECT COUNT(*) FROM backtest_runs"),
        "trades_total": one("SELECT COUNT(*) FROM trades"),
        # 之後可擴充：今日新增、最近7天、各 strategy 分佈等
    }