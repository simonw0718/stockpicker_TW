# backend/app/routers/watchlist.py
import json
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Path, Request
from app.db.conn import get_conn
from app.services.resolve import normalize_code_or_name
from app.models.watchlists import (
    WatchListCreate, WatchListUpdate, WatchListOut, WatchListItem
)

router = APIRouter()

# ---- 輕量限流 ----
from time import time
_bucket = {}
LIMIT = 60
WINDOW = 60.0

def _ratelimit(request: Request):
    ip = request.client.host if request.client else "unknown"
    now = time()
    win = int(now // WINDOW)
    key = (ip, win)
    _bucket[key] = _bucket.get(key, 0) + 1
    if _bucket[key] > LIMIT:
        raise HTTPException(status_code=429, detail={"error": {"code": "RATE_LIMIT", "message": "Too Many Requests"}})

def _err(code: str, msg: str):
    return HTTPException(status_code=400, detail={"error": {"code": code, "message": msg}})

# ---------- 正規化工具 ----------

def _ensure_code(s: str) -> str:
    code, choices = normalize_code_or_name(s)
    if code:
        return code
    if choices:
        raise _err("AMBIGUOUS_SYMBOL", f"多筆命中，請指定四碼：{[c['code'] for c in choices]}")
    raise _err("INVALID_SYMBOL", f"symbol not found: {s}")

def _normalize_symbols(items: List[Optional[str]]) -> List[str]:
    seen = set()
    out: List[str] = []
    for raw in (items or []):
        if raw is None:
            continue
        s = str(raw).strip()
        if not s:
            continue
        code = _ensure_code(s)
        if code in seen:
            continue   # <- 避免重複
        seen.add(code)
        out.append(code)
    return out

def _clean_name(raw_name: str) -> str:
    if raw_name is None:
        raise _err("INVALID_NAME", "name 不可為空")
    name = " ".join(raw_name.strip().split())
    if len(name) == 0:
        raise _err("INVALID_NAME", "name 不可為空字串")
    if len(name) > 100:
        name = name[:100]
    return name

# ---------- DB helpers ----------

def _fetch_items(conn, watchlist_id: int) -> List[WatchListItem]:
    rows = conn.execute(
        "SELECT symbol, position FROM watchlist_items WHERE watchlist_id = ? ORDER BY position, id",
        (watchlist_id,),
    ).fetchall()
    return [WatchListItem(symbol=r["symbol"], position=r["position"]) for r in rows]

def _to_out(conn, row) -> WatchListOut:
    return WatchListOut(
        id=row["id"],
        name=row["name"],
        items=_fetch_items(conn, row["id"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )

def _insert_items(conn, watchlist_id: int, codes: List[str]) -> None:
    # 依輸入順序給 position
    for idx, code in enumerate(codes):
        conn.execute(
            """
            INSERT INTO watchlist_items(watchlist_id, symbol, position, created_at, updated_at)
            VALUES(?, ?, ?, datetime('now'), datetime('now'))
            """,
            (watchlist_id, code, idx),
        )

# ---------- CRUD（/api/v1/watchlist 下） ----------

@router.post("", response_model=WatchListOut, status_code=201)
def create_watchlist(payload: WatchListCreate, request: Request):
    _ratelimit(request)
    name = _clean_name(payload.name)
    codes = _normalize_symbols(payload.symbols)

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO watchlist(name, owner, meta, created_at, updated_at)
        VALUES(?, NULL, NULL, datetime('now'), datetime('now'))
        """,
        (name,),
    )
    wl_id_raw = cur.lastrowid
    if wl_id_raw is None:
        # 這在 SQLite 正常情況不會發生，但保險起見加個守衛
        raise RuntimeError("failed to get lastrowid after INSERT watchlist")
    wl_id: int = int(wl_id_raw)
    _insert_items(conn, wl_id, codes)
    conn.commit()

    row = conn.execute("SELECT * FROM watchlist WHERE id = ?", (wl_id,)).fetchone()
    return _to_out(conn, row)

@router.get("", response_model=List[WatchListOut])
def list_watchlists():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM watchlist ORDER BY id").fetchall()
    return [_to_out(conn, r) for r in rows]

@router.get("/{list_id}", response_model=WatchListOut)
def get_watchlist(list_id: int = Path(..., ge=1)):
    conn = get_conn()
    row = conn.execute("SELECT * FROM watchlist WHERE id = ?", (list_id,)).fetchone()
    if not row:
        raise _err("NOT_FOUND", f"watchlist id not found: {list_id}")
    return _to_out(conn, row)

@router.patch("/{list_id}", response_model=WatchListOut)
def update_watchlist(list_id: int, payload: WatchListUpdate, request: Request):
    _ratelimit(request)
    conn = get_conn()
    row = conn.execute("SELECT * FROM watchlist WHERE id = ?", (list_id,)).fetchone()
    if not row:
        raise _err("NOT_FOUND", f"watchlist id not found: {list_id}")

    # name
    name = _clean_name(payload.name) if payload.name is not None else row["name"]
    conn.execute(
        "UPDATE watchlist SET name=?, updated_at=datetime('now') WHERE id=?",
        (name, list_id),
    )

    # items（若提供 symbols，採「全刪重建」以保序）
    if payload.symbols is not None:
        codes = _normalize_symbols(payload.symbols)
        conn.execute("DELETE FROM watchlist_items WHERE watchlist_id = ?", (list_id,))
        _insert_items(conn, list_id, codes)

    conn.commit()
    row = conn.execute("SELECT * FROM watchlist WHERE id = ?", (list_id,)).fetchone()
    return _to_out(conn, row)

@router.delete("/{list_id}", status_code=204)
def delete_watchlist(list_id: int, request: Request):
    _ratelimit(request)
    conn = get_conn()
    cur = conn.execute("DELETE FROM watchlist WHERE id = ?", (list_id,))
    conn.commit()
    if cur.rowcount == 0:
        raise _err("NOT_FOUND", f"watchlist id not found: {list_id}")
    return