# backend/db/conn.py
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "data" / "app.db"

def get_conn() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH.as_posix())
    conn.row_factory = sqlite3.Row
    # 關鍵：開啟外鍵約束（SQLite 預設關閉）
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn