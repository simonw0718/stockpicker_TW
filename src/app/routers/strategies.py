# src/app/routers/strategies.py
from __future__ import annotations

import json
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Path, Body

from app.domain.strategies.validation import Strategy, ValidationError, format_validation_error
from app.repositories import strategies as repo

router = APIRouter()


# --------- 小工具 ---------
def _to_dict(model_or_dict: Any) -> Dict[str, Any]:
    """
    Pydantic v2: model_dump()
    Pydantic v1: dict()
    已是 dict: 原樣回傳
    其他：嘗試 __dict__
    """
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
        # 與 docs/api/errors.md 對齊
        raise HTTPException(status_code=422, detail=format_validation_error(exc))


# --------------------------------
# GET /  列表（極簡；此期非必要，可保留為簡單存活回應）
# --------------------------------
@router.get("/")
def list_strategies():
    # Phase 1C 最小需求不要求列表，先回空集合
    return {"items": []}


# --------------------------------
# POST /strategies/validate : Schema 驗證（1A已提供，這裡整合保留）
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
# 422: schema 錯誤
# 409: name+version 衝突（repo 會 raise 專用格式）
# --------------------------------
@router.post("", status_code=201)
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
# GET /{id}
# 200 / 404
# --------------------------------
@router.get("/{id}")
def get_strategy(id: int = Path(..., ge=1)):
    row = repo.get_by_id(id)
    if not row:
        raise HTTPException(
            status_code=404,
            detail={"status": 404, "errors": [{"code": "not_found", "message": "strategy not found"}]}
        )

    # payload 內存的是完整策略 JSON 字串
    try:
        payload = json.loads(row["payload"])
    except Exception:
        payload = {}

    # 與先前 in-memory 行為一致：回傳 id + 策略內容
    return {"id": row["id"], **payload}


# --------------------------------
# （可選）GET /?name=&version=
# --------------------------------
@router.get("")
def get_strategy_by_nv(
    name: Optional[str] = Query(None),
    version: Optional[str] = Query(None),
):
    if not name or not version:
        return {"error": {"code": "BAD_REQUEST", "message": "name and version are required"}}
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


# --------------------------------
# PUT /{id}  Update
# 200 / 404 / 409 / 422
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

    # 先驗證 schema
    s_model = _validate_strategy_dict(body["strategy"])
    s = _to_dict(s_model)

    # 交給 repo（若改名/改版造成衝突，repo 會 raise 409）
    row = repo.update(id, s)  # 回傳 DB row（含 payload）
    try:
        payload = json.loads(row["payload"])
    except Exception:
        payload = {}

    # 維持簡潔回應（測試只在意成功與否；如需完整可改成 {"id": id, **payload}）
    return {"id": id, "name": payload.get("name"), "version": payload.get("version")}


# --------------------------------
# DELETE /{id}  邏輯刪除
# 204 / 404
# --------------------------------
@router.delete("/{id}", status_code=204)
def delete_strategy(id: int):
    repo.logical_delete(id)  # 找不到/已刪 → 404 由 repo raise
    return


# --------------------------------
# POST /{id}/validate  用既有策略驗證可執行性（本期 stub）
# 200 / 404 / 422（若 payload 無法被重建成合法模型）
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

    # Phase 1C：僅重跑 schema（後續可接實際可執行性檢查）
    _ = _validate_strategy_dict(payload)
    return {"ok": True, "id": id}