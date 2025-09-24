from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def list_alerts():
    """
    Phase0 stub: 回傳空警示清單
    """
    return {"items": []}