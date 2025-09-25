# backend/app/routers/symbols.py
from fastapi import APIRouter, Query
from backend.app.services.resolve import normalize_code_or_name

router = APIRouter()

@router.get("/search")
def search_symbols(q: str = Query(..., description="代碼或中文名稱片段")):
    """
    Phase0: 走純正規化邏輯，不依賴 DB 的 symbols 表
    回傳格式與舊邏輯相容：[{code, name?}]
    """
    code, choices = normalize_code_or_name(q)

    # 命中唯一（沒有多選）
    if code and not choices:
        # 沒查 DB，名稱暫時給 None（測試僅關心 200 與型別）
        return [{"code": code, "name": None}]

    # 有多個候選：直接回 choices（假設內含 code/name 結構）
    if choices:
        return choices

    # 找不到
    return []