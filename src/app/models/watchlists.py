# arc/app/models/watchlists.py
from typing import List, Optional
from pydantic import BaseModel, Field

class WatchListItem(BaseModel):
    symbol: str = Field(..., min_length=1, description="股票代碼（四碼數字），會經過正規化")
    position: int = Field(0, description="排序位置（整數，預設 0）")

class WatchListCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    # 輸入端仍支援 symbols（舊格式），方便前端直接丟 list
    symbols: List[Optional[str]] = Field(
        default_factory=list,
        description="symbols 欄位用於快速新增，後端會轉換成 watchlist_items"
    )

class WatchListUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    symbols: Optional[List[Optional[str]]] = Field(
        None,
        description="若提供，後端會重建對應的 watchlist_items；若不帶此欄位則不變更"
    )

class WatchListOut(BaseModel):
    id: int
    name: str
    items: List[WatchListItem] = Field(
        default_factory=list,
        description="watchlist_items，含 symbol 與排序 position"
    )
    created_at: str
    updated_at: str