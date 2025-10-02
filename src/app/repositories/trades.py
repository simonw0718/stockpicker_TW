# src/app/repositories/trades.py
from typing import List, Tuple, Dict, Any
from app.db.conn import get_conn

ALLOWED_ORDER = {"asc", "desc"}
ALLOWED_ORDER_BY = {"entry_ts", "exit_ts", "pnl", "pnl_pct", "symbol"}

class TradesRepo:
    def list_by_run(self, db, run_id: int, order_by: str, order: str, limit: int, offset: int) -> Tuple[list[Dict[str, Any]], int]:
        conn = db or get_conn()
        cur = conn.cursor()

        if order_by not in ALLOWED_ORDER_BY:
            order_by = "entry_ts"
        order = order if order in ALLOWED_ORDER else "asc"

        total = cur.execute("SELECT COUNT(*) AS c FROM trades WHERE run_id=?", (run_id,)).fetchone()["c"]

        rows = cur.execute(
            f"""
            SELECT id, run_id, symbol, side, entry_ts, entry_price, exit_ts, exit_price, size, pnl, pnl_pct, mae, mfe, tags, notes
              FROM trades
             WHERE run_id=?
             ORDER BY {order_by} {order}
             LIMIT ? OFFSET ?
            """,
            (run_id, limit, offset),
        ).fetchall()

        items = [
            {
                "trade_id": r["id"],
                "symbol": r["symbol"],
                "side": r["side"],
                "qty": r["size"],
                "entry_ts": r["entry_ts"],
                "entry_px": r["entry_price"],
                "exit_ts": r["exit_ts"],
                "exit_px": r["exit_price"],
                "pnl": r["pnl"],
                "pnl_pct": r["pnl_pct"],
                "mae": r["mae"],
                "mfe": r["mfe"],
                "tags": r["tags"],
                "notes": r["notes"],
            }
            for r in rows
        ]
        return items, int(total)