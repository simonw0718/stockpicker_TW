# tests/test_schema_v2.py
import sqlite3
from app.db import migrate_v2

def test_schema_v2_tables(tmp_path):
    db_path = tmp_path / "app.db"
    # 初始化測試用 DB
    con = sqlite3.connect(db_path)
    with open(migrate_v2.SCHEMA_PATH, "r", encoding="utf-8") as f:
        con.executescript(f.read())

    # 驗證表存在
    cur = con.cursor()
    for table in [
        "strategies", "params", "signals", "backtest_runs", 
        "trades", "alerts", "watchlist", "watchlist_items"
    ]:
        cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';")
        assert cur.fetchone() is not None, f"Table {table} missing"
    con.close()