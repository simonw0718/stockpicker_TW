# src/app/routers/strategies.py
from __future__ import annotations
import uuid
from typing import Dict, Tuple, Optional
from fastapi import APIRouter, HTTPException, Query, Path, Body

from app.domain.strategies.validation import Strategy, ValidationError, format_validation_error

router = APIRouter()

# --- in-memory repo（Phase1C 暫存，之後替換 DB） ---
_DB: Dict[str, Dict] = {}                 # id -> {strategy: dict, deleted_at: Optional[str]}
_IDX: Dict[Tuple[str, str], str] = {}     # (name, version) -> id

def _ensure_not_conflict(name: str, version: str, *, exclude_id: Optional[str] = None) -> None:
    k = (name, version)
    if k in _IDX:
        if exclude_id is None or _IDX[k] != exclude_id:
            # 已存在相同 name+version
            raise HTTPException(status_code=409, detail={"error": {"code": "CONFLICT", "message": "name+version already exists"}})

def _get_alive(id_: str) -> Dict:
    row = _DB.get(id_)
    if not row or row.get("deleted_at"):
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": f"strategy not found: {id_}"}})
    return row

# --- Utilities ---
def _validate_strategy_dict(payload: dict) -> Strategy:
    try:
        return Strategy(**payload)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=format_validation_error(exc))

# --------------------------------
# GET /  列表（極簡）
# --------------------------------
@router.get("/")
def list_strategies():
    items = []
    for sid, row in _DB.items():
        if row.get("deleted_at"):
            continue
        s = row["strategy"]
        items.append({"id": sid, "name": s["name"], "version": s["version"]})
    return {"items": items}

# --------------------------------
# POST /strategies/validate  (1A 已有：這裡整合保留)
# body: { "strategy": { ... } }
# --------------------------------
@router.post("/validate")
def validate_strategy(body: dict = Body(...)):
    if "strategy" not in body:
        raise HTTPException(status_code=422, detail={"status": 422, "errors": [{"path":"strategy","code":"missing_required","message":"field required"}]})
    _ = _validate_strategy_dict(body["strategy"])
    return {"ok": True}

# --------------------------------
# POST /  Create
# body: { "strategy": { ... } }
# 422: schema 錯誤
# 409: name+version 衝突
# --------------------------------
@router.post("", status_code=201)
def create_strategy(body: dict = Body(...)):
    if "strategy" not in body:
        raise HTTPException(status_code=422, detail={"status": 422, "errors": [{"path":"strategy","code":"missing_required","message":"field required"}]})
    s_model = _validate_strategy_dict(body["strategy"])
    s = s_model.dict()

    _ensure_not_conflict(s["name"], s["version"])
    sid = str(uuid.uuid4())
    _DB[sid] = {"strategy": s, "deleted_at": None}
    _IDX[(s["name"], s["version"])] = sid
    return {"id": sid, "name": s["name"], "version": s["version"]}

# --------------------------------
# GET /{id}  或  GET /?name=&version=
# --------------------------------
@router.get("/{id}")
def get_strategy(
    id: str = Path(..., description="strategy id"),
):
    row = _get_alive(id)
    return {"id": id, **row["strategy"]}

@router.get("")
def get_strategy_by_nv(
    name: Optional[str] = Query(None),
    version: Optional[str] = Query(None),
):
    if not name or not version:
        return {"error": {"code": "BAD_REQUEST", "message": "name and version are required"}}
    sid = _IDX.get((name, version))
    if not sid:
        raise HTTPException(status_code=404, detail={"error": {"code": "NOT_FOUND", "message": "strategy not found"}})
    row = _get_alive(sid)
    return {"id": sid, **row["strategy"]}

# --------------------------------
# PUT /{id}  Update（需先通過 1A 驗證，再更新；可更名/改版，處理 409）
# --------------------------------
@router.put("/{id}")
def update_strategy(id: str, body: dict = Body(...)):
    row = _get_alive(id)
    if "strategy" not in body:
        raise HTTPException(status_code=422, detail={"status": 422, "errors": [{"path":"strategy","code":"missing_required","message":"field required"}]})

    s_model = _validate_strategy_dict(body["strategy"])
    s = s_model.dict()

    # 若改了 name+version，要檢查衝突
    old = row["strategy"]
    if (s["name"], s["version"]) != (old["name"], old["version"]):
        _ensure_not_conflict(s["name"], s["version"], exclude_id=id)
        # 更新 index
        _IDX.pop((old["name"], old["version"]), None)
        _IDX[(s["name"], s["version"])] = id

    row["strategy"] = s
    return {"id": id, "name": s["name"], "version": s["version"]}

# --------------------------------
# DELETE /{id}  邏輯刪除
# --------------------------------
@router.delete("/{id}", status_code=204)
def delete_strategy(id: str):
    row = _get_alive(id)
    row["deleted_at"] = "now"   # Phase1C 先不記實際時間
    return

# --------------------------------
# POST /{id}/validate  用既有策略驗證能否執行（這期先做 schema validate）
# --------------------------------
@router.post("/{id}/validate")
def validate_existing(id: str):
    row = _get_alive(id)
    # Phase1C：僅重跑 schema；後續可以接 1B 的 calc 做更實際檢查
    _validate_strategy_dict(row["strategy"])
    return {"ok": True, "id": id}