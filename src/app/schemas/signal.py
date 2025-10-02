# src/app/schemas/signal.py
from typing import Optional, List
from pydantic import BaseModel
from .common import Page, TimeOrder

class SignalItem(BaseModel):
    signal_id: str
    ts: str
    symbol: str
    strategy_id: str
    strategy_version: int
    params_hash: str
    score: float
    features: dict | None = None
    source: str
    run_id: str | None = None

class SignalsResponse(BaseModel):
    items: List[SignalItem]
    total: int
    limit: int
    offset: int