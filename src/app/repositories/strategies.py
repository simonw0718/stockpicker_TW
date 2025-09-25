# src/app/repositories/strategies.py
from typing import Optional, Dict, Any
from app.db.conn import get_conn
import json
from fastapi import HTTPException

def create(strategy: Dict[str, Any]) -> Dict[str, Any]:
    name = strategy.get("name")
    version = strategy.get("version")
    if not name or not version:
        raise HTTPException(status_code=422, detail={"error": {"code": "MISSING_FIELD", "message": "name/version required"}})

    conn = get_conn()
    cur = conn.cursor()

    # 衝突檢查
    row = cur.execute(
        "SELECT id FROM strategies WHERE name=? AND version=? AND deleted_at IS NULL",
        (name, version)
    ).fetchone()
    if row:
        raise HTTPException(status_code=409, detail={"status":409,"errors":[{"code":"conflict","message":"name+version exists"}]})

    cur.execute(
        """
        INSERT INTO strategies (name, version, description, payload, created_at, updated_at)
        VALUES (?, ?, ?, ?, datetime('now'), datetime('now'))
        """,
        (name, version, strategy.get("description"), json.dumps(strategy))
    )
    new_id = cur.lastrowid
    conn.commit()
    return {"id": new_id, "name": name, "version": version}

def get_by_id(id: int) -> Optional[Dict[str, Any]]:
    conn = get_conn()
    row = conn.execute("SELECT * FROM strategies WHERE id=? AND deleted_at IS NULL", (id,)).fetchone()
    return dict(row) if row else None

def get_by_name_version(name: str, version: str) -> Optional[Dict[str, Any]]:
    conn = get_conn()
    row = conn.execute(
        "SELECT * FROM strategies WHERE name=? AND version=? AND deleted_at IS NULL",
        (name, version)
    ).fetchone()
    return dict(row) if row else None

def update(id: int, strategy: Dict[str, Any]) -> Dict[str, Any]:
    conn = get_conn()
    cur = conn.cursor()
    row = cur.execute("SELECT * FROM strategies WHERE id=? AND deleted_at IS NULL", (id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail={"status":404,"errors":[{"code":"not_found","message":"strategy not found"}]})

    cur.execute(
        "UPDATE strategies SET payload=?, description=?, updated_at=datetime('now') WHERE id=?",
        (json.dumps(strategy), strategy.get("description"), id)
    )
    conn.commit()
    return get_by_id(id)

def logical_delete(id: int) -> None:
    conn = get_conn()
    cur = conn.cursor()
    row = cur.execute("SELECT id FROM strategies WHERE id=? AND deleted_at IS NULL", (id,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail={"status":404,"errors":[{"code":"not_found","message":"strategy not found"}]})

    cur.execute("UPDATE strategies SET deleted_at=datetime('now') WHERE id=?", (id,))
    conn.commit()