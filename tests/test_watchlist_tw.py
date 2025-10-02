import sqlite3
import json
import pytest
from fastapi.testclient import TestClient

from src.app.main import app
from src.app.db.migrate_v2 import init_db
from src.app.db.conn import get_conn, DB_PATH

client = TestClient(app)

@pytest.fixture(autouse=True, scope="function")
def fresh_db():
    init_db()
    yield

def test_create_watchlist_tw_codes_only():
    # 建立
    payload = {"name": "TechTW", "symbols": ["2330", "2317"]}
    r = client.post("/api/v1/watchlist/", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()

    # 僅兩檔、且無 2882
    syms = [it["symbol"] for it in data["items"]]
    assert syms == ["2330", "2317"]

    # position 正確
    pos = [it["position"] for it in data["items"]]
    assert pos == [0, 1]

def test_list_watchlist_after_create():
    # 先建
    client.post("/api/v1/watchlist/", json={"name": "TechTW", "symbols": ["2330", "2317"]})
    r = client.get("/api/v1/watchlist/")
    assert r.status_code == 200
    arr = r.json()
    assert len(arr) == 1
    assert [it["symbol"] for it in arr[0]["items"]] == ["2330", "2317"]