# src/app/routers/strategies.py
from __future__ import annotations

import json
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Path, Body

from app.domain.strategies.validation import Strategy, ValidationError, format_validation_error
from app.repositories import strategies as repo

# 統一使用 prefix，避免空路徑錯誤
router = APIRouter(prefix="/api/v1/strategies", tags=["strategies"])

# --------- 小工具 ---------
def _to_dict(model_or_dict: Any) -> Dict[str, Any]:
    if isinstance(model_or_dict, dict):
        return model_or_dict
    if hasattr(model_or_dict, "model_dump"):
        return model_or_dict.model_dump()  # pydantic v2
    if hasattr(model_or_dict, "dict"):
        return model_or_dict.dict()        # pydantic v1
    return dict(getattr(model_or_dict, "__dict__", {}))

def _validate_strategy_dict(payload: dict) -> Strategy:
    try:
        return Strategy(**payload)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=format_validation_error(exc))

# --------------------------------
# GET /  列表或 name+version 查詢（二合一）
# - 無參數：回空清單（Phase 1C 極簡）
# - 有 name+version：回單筆（與先前 /?name=&version= 行為一致）
# --------------------------------
@router.get("/")
def list_or_get(
    name: Optional[str] = Query(None),
    version: Optional[str] = Query(None),
):
    if name and version:
        row = repo.get_by_name_version(name, version)
        if not row:
            raise HTTPException(
                status_code=404,
                detail={"status": 404, "errors": [{"code": "not_found", "message": "strategy not found"}]}
            )
        try:
            payload = json.loads(row["payload"])
        except Exception:
            payload = {}
        return {"id": row["id"], **payload}
    # 無參數 → 最小列表回應
    return {"items": []}

# --------------------------------
# POST /validate : Schema 驗證
# body: { "strategy": { ... } }
# --------------------------------
@router.post("/validate")
def validate_strategy(body: dict = Body(...)):
    if "strategy" not in body:
        raise HTTPException(
            status_code=422,
            detail={"status": 422, "errors": [{
                "path": "strategy", "code": "missing_required", "message": "field required"
            }]}
        )
    _ = _validate_strategy_dict(body["strategy"])
    return {"ok": True}

# --------------------------------
# POST /  Create
# body: { "strategy": { ... } }
# 422: schema 錯誤；409: name+version 衝突
# --------------------------------
@router.post("/", status_code=201)
def create_strategy(body: dict = Body(...)):
    if "strategy" not in body:
        raise HTTPException(
            status_code=422,
            detail={"status": 422, "errors": [{
                "path": "strategy", "code": "missing_required", "message": "field required"
            }]}
        )
    s_model = _validate_strategy_dict(body["strategy"])
    s = _to_dict(s_model)
    rec = repo.create(s)  # -> {"id": int, "name": str, "version": str}
    return {"id": rec["id"]}

# --------------------------------
# GET /{id}  讀單筆
# --------------------------------
@router.get("/{id}")
def get_strategy(id: int = Path(..., ge=1)):
    row = repo.get_by_id(id)
    if not row:
        raise HTTPException(
            status_code=404,
            detail={"status": 404, "errors": [{"code": "not_found", "message": "strategy not found"}]}
        )
    try:
        payload = json.loads(row["payload"])
    except Exception:
        payload = {}
    return {"id": row["id"], **payload}

# --------------------------------
# PUT /{id}  Update
# --------------------------------
@router.put("/{id}")
def update_strategy(id: int, body: dict = Body(...)):
    if "strategy" not in body:
        raise HTTPException(
            status_code=422,
            detail={"status": 422, "errors": [{
                "path": "strategy", "code": "missing_required", "message": "field required"
            }]}
        )
    s_model = _validate_strategy_dict(body["strategy"])
    s = _to_dict(s_model)
    row = repo.update(id, s)
    try:
        payload = json.loads(row["payload"])
    except Exception:
        payload = {}
    return {"id": id, "name": payload.get("name"), "version": payload.get("version")}

# --------------------------------
# DELETE /{id}  邏輯刪除
# --------------------------------
@router.delete("/{id}", status_code=204)
def delete_strategy(id: int):
    repo.logical_delete(id)
    return

# --------------------------------
# POST /{id}/validate  用既有策略驗證（本期 stub）
# --------------------------------
@router.post("/{id}/validate")
def validate_existing(id: int):
    row = repo.get_by_id(id)
    if not row:
        raise HTTPException(
            status_code=404,
            detail={"status": 404, "errors": [{"code": "not_found", "message": "strategy not found"}]}
        )
    try:
        payload = json.loads(row["payload"])
    except Exception:
        payload = {}
    _ = _validate_strategy_dict(payload)
    return {"ok": True, "id": id}