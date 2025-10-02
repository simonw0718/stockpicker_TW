# src/app/schemas/scan.py
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class ScanCreate(BaseModel):
    strategy_id: str
    symbols: List[str] = Field(..., min_items=1, max_items=500)
    start_date: str
    end_date: str
    timeframe: str = "1D"
    params_snapshot: Dict[str, Any]

class ScanAccepted(BaseModel):
    job_id: str
    status: str = "pending"