from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def list_strategies():
    """
    Phase0 stub: 回傳空策略清單
    """
    return {"items": []}