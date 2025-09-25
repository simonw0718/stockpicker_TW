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
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        con.executescript(f.read())
    con.commit()
    con.close()