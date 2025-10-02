# src/app/repositories/alerts.py
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime
from app.db.conn import get_conn

# 對外參數名 → 真實欄位名 的映射（只開放這些欄位排序）
ORDER_BY_MAP: Dict[str, str] = {
    "ts": "last_triggered_ts",   # 對外 ts = 內部 last_triggered_ts
    "status": "status",
    "symbol": "symbol",
    "created_at": "created_at",
    "updated_at": "updated_at",
}
ALLOWED_ORDER_BY = set(ORDER_BY_MAP.keys())
ALLOWED_STATUS = {"pending", "sent", "failed", "skipped"}


def _alerts_has_columns(conn, cols: List[str]) -> bool:
    """
    檢查 alerts 表是否同時具備指定欄位（用於 attempts/last_error/last_sent_ts 相容處理）
    """
    cur = conn.execute("PRAGMA table_info('alerts')")
    have = {r["name"] for r in cur.fetchall()}
    return all(c in have for c in cols)


class AlertsRepo:
    # --- 由 signal 建立一筆 alert（最小可用 stub） ---
    def create_from_signal(self, db, payload: Dict[str, Any]) -> int:
        """
        以 signal-like payload 產生一筆 alerts。
        目前 schema 無 signal_id/payload 欄位，僅塞入必要欄位：
          - symbol            ← payload["symbol"]
          - condition         ← f"strategy:{strategy_id}:{signal_type}"
          - timeframe         ← payload.get("timeframe", "1D")
          - status            ← "pending"
          - last_triggered_ts ← payload["ts"]
          - channel           ← "webhook"
        """
        required = ("strategy_id", "symbol", "ts", "signal_type")
        for k in required:
            if k not in payload:
                raise ValueError(f"missing required field: {k}")

        conn = db or get_conn()
        cur = conn.cursor()

        strategy_id = int(payload["strategy_id"])
        symbol = str(payload["symbol"])
        ts = str(payload["ts"])
        timeframe = str(payload.get("timeframe", "1D"))
        sig_type = str(payload["signal_type"])

        condition = f"strategy:{strategy_id}:{sig_type}"
        status = "pending"
        channel = "webhook"

        cur.execute(
            """
            INSERT INTO alerts(symbol, condition, timeframe, status, last_triggered_ts, channel, created_at, updated_at)
            VALUES(?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """,
            (symbol, condition, timeframe, status, ts, channel),
        )
        new_id = cur.lastrowid
        if new_id is None:
            raise RuntimeError("insert alert failed: no lastrowid")
        conn.commit()
        return int(new_id)

    def list_alerts(
        self,
        db,
        *,
        start_ts: Optional[str],
        end_ts: Optional[str],
        symbol: Optional[str],
        strategy_id: Optional[int],         # 目前表內沒有此欄，忽略
        webhook_status: Optional[str],      # 對映到現有 alerts.status
        order_by: str = "ts",
        order: str = "desc",
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Dict[str, Any]], int]:
        conn = db or get_conn()
        cur = conn.cursor()

        # ---- 排序處理 ----
        ob_key = str(order_by).lower().strip() if order_by is not None else "ts"
        if ob_key not in ALLOWED_ORDER_BY:
            ob_key = "ts"
        order_by_col = ORDER_BY_MAP[ob_key]
        order_dir = "ASC" if str(order).lower() == "asc" else "DESC"

        # ---- 篩選條件 ----
        filters: List[str] = []
        params: List[Any] = []

        if start_ts:
            filters.append("last_triggered_ts >= ?")
            params.append(start_ts)
        if end_ts:
            filters.append("last_triggered_ts <= ?")
            params.append(end_ts)
        if symbol:
            filters.append("symbol = ?")
            params.append(symbol)

        # 目前 alerts 表沒有 strategy_id 欄位；忽略該條件
        _ = strategy_id  # noqa

        # webhook_status 正規化與白名單
        if webhook_status is not None:
            st = str(webhook_status).lower().strip()
            if st in ALLOWED_STATUS:
                filters.append("status = ?")
                params.append(st)

        where_sql = f"WHERE {' AND '.join(filters)}" if filters else ""

        # ---- 分頁保護 ----
        try:
            limit = max(0, min(int(limit), 200))
        except Exception:
            limit = 50
        try:
            offset = max(0, int(offset))
        except Exception:
            offset = 0

        # ---- total ----
        total_row = cur.execute(
            f"SELECT COUNT(*) AS c FROM alerts {where_sql}",
            params
        ).fetchone()
        total = int(total_row["c"]) if total_row else 0

        # ---- 列表 ----
        rows = cur.execute(
            f"""
            SELECT id, symbol, condition, timeframe, status, last_triggered_ts,
                   channel, created_at, updated_at
              FROM alerts
              {where_sql}
             ORDER BY {order_by_col} {order_dir}
             LIMIT ? OFFSET ?
            """,
            (*params, limit, offset),
        ).fetchall()

        items: List[Dict[str, Any]] = [
            {
                "alert_id": r["id"],
                "symbol": r["symbol"],
                "condition": r["condition"],
                "timeframe": r["timeframe"],
                "status": r["status"],                 # 對應 webhook_status
                "last_triggered_ts": r["last_triggered_ts"],
                "channel": r["channel"],
                "created_at": r["created_at"],
                "updated_at": r["updated_at"],
            }
            for r in rows
        ]
        return items, total

    # --- 發送（stub，向後相容無 attempts/last_error/last_sent_ts 也能用） ---
    def send_alert(
        self,
        db,
        alert_id: int,
        *,
        outcome: str = "sent",
        error: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        模擬將 alert 送到 webhook：
        - outcome = 'sent' | 'failed'（其他值一律視為 'sent'）
        - 若表有 attempts/last_error/last_sent_ts 欄位，則 attempts += 1、last_error 更新、last_sent_ts=now；
          否則僅更新 status/updated_at
        回傳最新 alert 記錄；不存在則回 None。
        """
        conn = db or get_conn()
        cur = conn.cursor()

        row = cur.execute("SELECT id FROM alerts WHERE id = ?", (alert_id,)).fetchone()
        if not row:
            return None

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        outcome = outcome if outcome in ("sent", "failed") else "sent"

        has_extra = _alerts_has_columns(conn, ["attempts", "last_error", "last_sent_ts"])

        if has_extra:
            cur.execute(
                """
                UPDATE alerts
                   SET status = ?,
                       attempts = COALESCE(attempts, 0) + 1,
                       last_error = CASE WHEN ? IS NULL THEN last_error ELSE ? END,
                       updated_at = ?,
                       last_sent_ts = ?
                 WHERE id = ?
                """,
                (outcome, error, error, now, now, alert_id),
            )
        else:
            cur.execute(
                """
                UPDATE alerts
                   SET status = ?, updated_at = ?
                 WHERE id = ?
                """,
                (outcome, now, alert_id),
            )
        conn.commit()

        # 取回最新
        r = conn.execute(
            """
            SELECT id, symbol, condition, timeframe, status, last_triggered_ts,
                   channel, created_at, updated_at
              FROM alerts WHERE id = ?
            """,
            (alert_id,),
        ).fetchone()

        result: Dict[str, Any] = {
            "alert_id": r["id"],
            "symbol": r["symbol"],
            "condition": r["condition"],
            "timeframe": r["timeframe"],
            "status": r["status"],
            "last_triggered_ts": r["last_triggered_ts"],
            "channel": r["channel"],
            "created_at": r["created_at"],
            "updated_at": r["updated_at"],
        }

        # 若表真的有 attempts/last_error/last_sent_ts，再補帶回傳
        if has_extra:
            r2 = conn.execute(
                "SELECT attempts, last_error, last_sent_ts FROM alerts WHERE id = ?",
                (alert_id,),
            ).fetchone()
            result["attempts"] = r2["attempts"]
            result["last_error"] = r2["last_error"]
            result["last_sent_ts"] = r2["last_sent_ts"]

        return result