# src/app/db/migrate_v2.py
from __future__ import annotations
import sqlite3
from pathlib import Path
from .conn import DB_PATH

# 讓測試能直接引用 schema 檔路徑
SCHEMA_PATH: Path = Path(__file__).with_name("schema_v2.sql")

def init_db() -> None:
    """
    測試前初始化資料庫：
    - 確保 data/ 目錄存在
    - 若既有 app.db，直接刪除以得到全新乾淨狀態（避免殘留資料造成 409/UNIQUE 衝突）
    - 套用 schema_v2.sql
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()  # 乾脆刪掉舊 DB，確保純淨

    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        con.executescript(f.read())
    con.commit()
    con.close()

def patch_db_in_place() -> None:
    """
    不重建 DB 的情況下，安全補 alerts 欄位（attempts/last_error/last_sent_ts）。
    可在手動維運時呼叫。
    """
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    _safe_add_columns_alerts(con)
    con.close()

def _safe_add_columns_alerts(conn: sqlite3.Connection) -> None:
    """
    在「不重建 DB」的情況下，安全補 alerts 欄位：
      - attempts INTEGER DEFAULT 0
      - last_error TEXT
      - last_sent_ts TEXT
    並把 attempts 既有資料補 0（避免 NULL）。
    """
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cols = {r["name"] for r in cur.execute("PRAGMA table_info(alerts)").fetchall()}

    try:
        if "attempts" not in cols:
            cur.execute("ALTER TABLE alerts ADD COLUMN attempts INTEGER DEFAULT 0")
    except Exception:
        pass

    try:
        if "last_error" not in cols:
            cur.execute("ALTER TABLE alerts ADD COLUMN last_error TEXT")
    except Exception:
        pass

    try:
        if "last_sent_ts" not in cols:
            cur.execute("ALTER TABLE alerts ADD COLUMN last_sent_ts TEXT")
    except Exception:
        pass

    try:
        cur.execute("UPDATE alerts SET attempts = COALESCE(attempts, 0)")
    except Exception:
        pass

    conn.commit()

if __name__ == "__main__":
    # 與你現有流程相容：python -m src.app.db.migrate_v2
    init_db()