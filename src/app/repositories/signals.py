# src/app/repositories/singals.py
from typing import List, Optional, Tuple, Dict, Any
from app.db.conn import get_conn
import uuid, json
import math

ALLOWED_ORDER_BY = {"ts", "strength", "symbol"}

def _to_json_text(v):
    if v is None:
        return None
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False)
    return v

def _maybe_parse_json_text(v):
    if v is None:
        return None
    if isinstance(v, (dict, list)):
        return v
    if isinstance(v, (bytes, bytearray)):
        v = v.decode("utf-8", errors="ignore")
    if isinstance(v, str):
        v = v.strip()
        if v.startswith("{") or v.startswith("["):
            try:
                return json.loads(v)
            except Exception:
                pass
    return v

def _normalize_strength(x) -> Optional[float]:
    """
    strength 正常化：
    - None/NaN → None
    - 其餘轉 float，並 clamp 到 [0,1]
    """
    if x is None:
        return None
    try:
        fx = float(x)
    except Exception:
        return None
    if math.isnan(fx):
        return None
    if fx < 0.0: fx = 0.0
    if fx > 1.0: fx = 1.0
    return fx

class SignalsRepo:
    # ---- Idempotent scan job 映射 ----
    def get_or_create_scan_job(self, db, key: str) -> str:
        conn = db or get_conn()
        cur = conn.cursor()
        try:
            row = cur.execute("SELECT job_id FROM scan_jobs WHERE key=?", (key,)).fetchone()
        except Exception:
            return uuid.uuid4().hex

        if row:
            return row["job_id"]
        job_id = uuid.uuid4().hex
        cur.execute(
            "INSERT INTO scan_jobs(key, job_id, created_at) VALUES(?, ?, datetime('now'))",
            (key, job_id),
        )
        conn.commit()
        return job_id

    def generate_job_id(self) -> str:
        return uuid.uuid4().hex

    def upsert_signal(self, db, item: Dict[str, Any]) -> int:
        """
        以 (strategy_id, symbol, timeframe, ts) 為唯一鍵做 UPSERT。
        需依賴 schema 的 UNIQUE INDEX ux_signals_key(strategy_id, symbol, timeframe, ts)。
        """
        conn = db or get_conn()
        cur = conn.cursor()

        strategy_id = int(item["strategy_id"])
        symbol = item["symbol"]
        ts = item["ts"]
        timeframe = item.get("timeframe", "1D")

        strength = _normalize_strength(item.get("strength"))
        meta_txt = _to_json_text(item.get("meta"))
        sig_type = item.get("signal_type")

        # 單條 UPSERT（SQLite）
        cur.execute(
            """
            INSERT INTO signals (strategy_id, symbol, timeframe, signal_type, strength, ts, meta, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            ON CONFLICT(strategy_id, symbol, timeframe, ts)
            DO UPDATE SET
                strength    = COALESCE(excluded.strength, signals.strength),
                signal_type = COALESCE(excluded.signal_type, signals.signal_type),
                meta        = COALESCE(excluded.meta, signals.meta)
            """,
            (strategy_id, symbol, timeframe, sig_type, strength, ts, meta_txt),
        )
        conn.commit()

        row = cur.execute(
            "SELECT id FROM signals WHERE strategy_id=? AND symbol=? AND timeframe=? AND ts=?",
            (strategy_id, symbol, timeframe, ts),
        ).fetchone()
        return int(row["id"])

    def list_signals(
        self,
        db,
        *,
        start_ts: Optional[str],
        end_ts: Optional[str],
        symbol: Optional[str],
        strategy_id: Optional[int],
        source: Optional[str],
        order_by: str = "ts",
        order: str = "desc",
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Dict], int]:
        conn = db or get_conn()
        cur = conn.cursor()

        if order_by not in ALLOWED_ORDER_BY:
            order_by = "ts"
        order = "desc" if str(order).lower() != "asc" else "asc"

        filters = []
        params: list[Any] = []
        if start_ts:
            filters.append("ts >= ?")
            params.append(start_ts)
        if end_ts:
            filters.append("ts <= ?")
            params.append(end_ts)
        if symbol:
            filters.append("symbol = ?")
            params.append(symbol)
        if strategy_id is not None:
            filters.append("strategy_id = ?")
            params.append(strategy_id)

        where = ("WHERE " + " AND ".join(filters)) if filters else ""
        total = cur.execute(f"SELECT COUNT(*) AS c FROM signals {where}", params).fetchone()["c"]

        rows = cur.execute(
            f"""
            SELECT id, strategy_id, symbol, timeframe, signal_type, strength, ts, meta, created_at
              FROM signals
              {where}
             ORDER BY {order_by} {order}
             LIMIT ? OFFSET ?
            """,
            (*params, limit, offset),
        ).fetchall()

        items = [
            {
                "signal_id": r["id"],
                "ts": r["ts"],
                "symbol": r["symbol"],
                "strategy_id": r["strategy_id"],
                "timeframe": r["timeframe"],
                "signal_type": r["signal_type"],
                "strength": r["strength"],
                "meta": _maybe_parse_json_text(r["meta"]),
                "created_at": r["created_at"],
            }
            for r in rows
        ]
        return items, int(total)

    def get_scan_job(self, db, job_id: str) -> Optional[Dict[str, Any]]:
        conn = db or get_conn()
        cur = conn.cursor()
        try:
            row = cur.execute(
                "SELECT key, job_id, created_at FROM scan_jobs WHERE job_id=?",
                (job_id,),
            ).fetchone()
        except Exception:
            return None
        if not row:
            return None
        return {
            "key": row["key"],
            "job_id": row["job_id"],
            "created_at": row["created_at"],
            "status": "pending",
            "symbols_total": 0,
            "symbols_done": 0,
            "started_at": None,
            "finished_at": None,
        }