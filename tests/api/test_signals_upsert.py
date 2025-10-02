# tests/api/test_signals_upsert.py
import json
from fastapi.testclient import TestClient
from app.main import app
from app.db import migrate_v2
from app.db.conn import DB_PATH

client = TestClient(app)

def setup_module():
    # 乾淨 DB
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    migrate_v2.init_db()

def test_signals_upsert_create_then_update():
    body = {
        "strategy_id": 1,
        "symbol": "2330",
        "ts": "2025-09-28 00:00:00",
        "timeframe": "1D",
        "signal_type": "buy",
        "strength": 0.7,
        "meta": {"note": "from stub"},
    }
    r1 = client.post("/api/v1/signals/upsert", json=body)
    assert r1.status_code == 201
    sid = r1.json()["signal_id"]

    # 查詢應有 0.7
    rlist = client.get("/api/v1/signals", params={"order_by":"strength","order":"desc","limit":5})
    assert rlist.status_code == 200
    items = rlist.json()["items"]
    assert any(i["signal_id"] == sid and i["strength"] == 0.7 for i in items)

    # 同鍵更新 -> 0.9
    body["strength"] = 0.9
    body["meta"] = {"note": "update"}
    r2 = client.post("/api/v1/signals/upsert", json=body)
    assert r2.status_code == 201
    assert r2.json()["signal_id"] == sid

    rtop = client.get("/api/v1/signals", params={"order_by":"ts","order":"desc","limit":1})
    top = rtop.json()["items"][0]
    assert top["signal_id"] == sid
    assert top["strength"] == 0.9
    assert top["meta"]["note"] == "update"