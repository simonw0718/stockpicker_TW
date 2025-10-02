# src/app/schemas/alert.py
from typing import Optional, List
from pydantic import BaseModel

class AlertItem(BaseModel):
    alert_id: str
    signal_id: str
    ts: str
    strategy_id: str
    symbol: str
    payload: dict
    webhook_status: str
    attempts: int
    last_error: str | None = None
    created_at: str

class AlertsResponse(BaseModel):
    items: list[AlertItem]
    total: int
    limit: int
    offset: int