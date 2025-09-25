# src/app/repositories/strategies.py
from typing import Optional, Dict, Any
import json
from fastapi import HTTPException

from app.db.conn import get_conn


def _dump_json(obj: Any) -> str:
    # 穩定 & 支援中文
    return json.dumps(obj, ensure_ascii=False, sort_keys=True)


def create(strategy: Dict[str, Any]) -> Dict[str, Any]:
    name = strategy.get("name")
    version = strategy.get("version")
    if not name or not version:
        raise HTTPException(
            status_code=422,
            detail={"error": {"code": "MISSING_FIELD", "message": "name/version required"}},
        )

    conn = get_conn()
    cur = conn.cursor()

    # 衝突檢查（同名同版且未被刪除）
    row = cur.execute(
        "SELECT id FROM strategies WHERE name=? AND version=? AND deleted_at IS NULL",
        (name, version),
    ).fetchone()
    if row:
        raise HTTPException(
            status_code=409,
            detail={"status": 409, "errors": [{"code": "conflict", "message": "name+version exists"}]},
        )

    # 寫入完整 payload
    cur.execute(
        """
        INSERT INTO strategies (name, version, description, payload, created_at, updated_at)
        VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
        """,
        (name, version, strategy.get("description"), _dump_json(strategy)),
    )
    new_id = cur.lastrowid

    # params 快照（可留空）
    params = strategy.get("params")
    if params is not None:
        updated = conn.execute(
            "UPDATE params SET params_json=?, updated_at=datetime('now') WHERE strategy_id=?",
            (_dump_json(params), new_id),
        ).rowcount
        if updated == 0:
            conn.execute(
                """
                INSERT INTO params (strategy_id, params_json, created_at, updated_at)
                VALUES (?, ?, datetime('now'), datetime('now'))
                """,
                (new_id, _dump_json(params)),
            )

    conn.commit()
    return {"id": new_id, "name": name, "version": version}


def get_by_id(id: int) -> Optional[Dict[str, Any]]:
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM strategies WHERE id=? AND deleted_at IS NULL",
        (id,),
    ).fetchone()
    return dict(row) if row else None


def get_by_name_version(name: str, version: str) -> Optional[Dict[str, Any]]:
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM strategies WHERE name=? AND version=? AND deleted_at IS NULL",
        (name, version),
    ).fetchone()
    return dict(row) if row else None


def update(id: int, strategy: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_conn()
    cur = conn.cursor()

    # 確認存在
    row = cur.execute(
        "SELECT * FROM strategies WHERE id=? AND deleted_at IS NULL",
        (id,),
    ).fetchone()
    if not row:
        raise HTTPException(
            status_code=404,
            detail={"status": 404, "errors": [{"code": "not_found", "message": "strategy not found"}]},
        )

    # 可能變更 name/version → 先做衝突檢查
    old_name, old_ver = row["name"], row["version"]
    new_name = strategy.get("name", old_name)
    new_ver = strategy.get("version", old_ver)

    if (new_name, new_ver) != (old_name, old_ver):
        dup = cur.execute(
            """
            SELECT id FROM strategies
            WHERE name=? AND version=? AND deleted_at IS NULL AND id<>?
            """,
            (new_name, new_ver, id),
        ).fetchone()
        if dup:
            raise HTTPException(
                status_code=409,
                detail={"status": 409, "errors": [{"code": "conflict", "message": "name+version exists"}]},
            )

    # 覆寫欄位與 payload/description
    cur.execute(
        """
        UPDATE strategies
        SET name=?, version=?, payload=?, description=?, updated_at=datetime('now')
        WHERE id=?
        """,
        (new_name, new_ver, _dump_json(strategy), strategy.get("description"), id),
    )

    # 覆寫 params 快照（若有提供）
    if "params" in strategy:
        params = strategy.get("params")
        if params is None:
            conn.execute("DELETE FROM params WHERE strategy_id=?", (id,))
        else:
            updated = conn.execute(
                "UPDATE params SET params_json=?, updated_at=datetime('now') WHERE strategy_id=?",
                (_dump_json(params), id),
            ).rowcount
            if updated == 0:
                conn.execute(
                    """
                    INSERT INTO params (strategy_id, params_json, created_at, updated_at)
                    VALUES (?, ?, datetime('now'), datetime('now'))
                    """,
                    (id, _dump_json(params)),
                )

    conn.commit()
    res = get_by_id(id)
    assert res is not None
    return res


def logical_delete(id: int) -> None:
    conn = get_conn()
    cur = conn.cursor()
    row = cur.execute(
        "SELECT id FROM strategies WHERE id=? AND deleted_at IS NULL",
        (id,),
    ).fetchone()
    if not row:
        raise HTTPException(
            status_code=404,
            detail={"status": 404, "errors": [{"code": "not_found", "message": "strategy not found"}]},
        )

    cur.execute("UPDATE strategies SET deleted_at=datetime('now') WHERE id=?", (id,))
    conn.commit()