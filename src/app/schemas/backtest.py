# src/app/schemas/backtest.py
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class Assumptions(BaseModel):
    exec: str = "T+1_open"
    fees: float = 0.0
    slippage: float = 0.0
    sizing_rule: str = "fixed"
    sizing_params: Dict[str, Any] = {}
    exit_overrides: Dict[str, Optional[float]] = {
        "stop_loss_pct": None, "take_profit_pct": None, "max_holding_days": None
    }

class BacktestCreate(BaseModel):
    strategy_id: str
    symbol: str
    timeframe: str = "1D"
    start_date: str
    end_date: str
    params_snapshot: Dict[str, Any]
    price_adjustment: str = "adjusted"
    assumptions: Assumptions = Assumptions()

class BacktestAccepted(BaseModel):
    run_id: str
    status: str = "pending"
    created_at: str

class MetricsSummary(BaseModel):
    win_rate: float
    total_pnl: float
    max_drawdown: float
    CAGR: float
    Sharpe: float

class BacktestRun(BaseModel):
    run_id: str
    strategy_id: str
    symbol: str
    timeframe: str
    price_adjustment: str
    start_date: str
    end_date: str
    assumptions: Assumptions
    metrics_summary: Optional[MetricsSummary] = None
    status: str
    created_at: str
    finished_at: Optional[str] = None