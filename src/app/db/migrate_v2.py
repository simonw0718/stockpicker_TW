# backend/db/migrate_v2.py
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[2]
DB_PATH = ROOT / "data" / "app.db"
SCHEMA_PATH = Path(__file__).parent / "schema_v2.sql"

def init_db():
    con = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        con.executescript(f.read())
    con.commit()
    con.close()
    print(f"Initialized DB at {DB_PATH}")

if __name__ == "__main__":
    init_db()