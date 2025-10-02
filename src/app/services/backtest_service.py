# src/app/services/backtest_service.py
import uuid, datetime as dt
from typing import Dict, Any

class BacktestService:
    def __init__(self, backtests_repo, trades_repo):
        self.backtests = backtests_repo
        self.trades = trades_repo

    def create_backtest(self, db, payload: Dict[str, Any]) -> Dict[str, Any]:
        run_id = str(uuid.uuid4())
        now = dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).isoformat()
        run = {
            "run_id": run_id,
            "status": "pending",
            "created_at": now,
            **payload
        }
        self.backtests.create_run(db, run)
        return {"run_id": run_id, "status": "pending", "created_at": now}

    def get_run_summary(self, db, run_id: str) -> Dict[str, Any] | None:
        return self.backtests.get_run(db, run_id)