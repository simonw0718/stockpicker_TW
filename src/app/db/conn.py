# src/app/db/conn.py
from pathlib import Path
import sqlite3

# 這個檔案位置：.../src/app/db/conn.py
# parents[0]=.../src/app/db, [1]=.../src/app, [2]=.../src, [3]=.../<repo-root>
PROJECT_ROOT = Path(__file__).resolve().parents[3]

DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = DATA_DIR / "app.db"

def get_conn():
    # 再次保險
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn
