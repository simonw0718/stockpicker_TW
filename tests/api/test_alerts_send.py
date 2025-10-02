from fastapi.testclient import TestClient
from app.main import app
from app.db.conn import get_conn

client = TestClient(app)

def _seed_one_alert():
    conn = get_conn()
    conn.execute("""
        INSERT INTO alerts(symbol, condition, timeframe, status, last_triggered_ts, channel, created_at, updated_at)
        VALUES('2330','strategy:1:buy','1D','pending','2025-09-28 00:00:00','webhook',datetime('now'),datetime('now'))
    """)
    # 關鍵：要 commit，否則另一條連線（API handler）看不到
    conn.commit()
    return int(conn.execute("SELECT last_insert_rowid() AS id").fetchone()["id"])

def test_alert_send_sent_then_failed():
    alert_id = _seed_one_alert()

    # sent
    r = client.post(f"/api/v1/alerts/{alert_id}/send", json={"outcome": "sent"})
    assert r.status_code == 200
    j = r.json()
    assert j["status"] == "sent"
    assert j.get("attempts", 0) >= 1

    # failed
    r = client.post(f"/api/v1/alerts/{alert_id}/send", json={"outcome": "failed", "error": "webhook 500"})
    assert r.status_code == 200
    j = r.json()
    assert j["status"] == "failed"
    assert j.get("attempts", 0) >= 2
    assert j.get("last_error") == "webhook 500"

def test_alert_send_illegal_outcome_treated_as_sent():
    alert_id = _seed_one_alert()
    r = client.post(f"/api/v1/alerts/{alert_id}/send", json={"outcome": "weird"})
    assert r.status_code == 200
    j = r.json()
    assert j["status"] == "sent"
    assert j.get("attempts", 0) >= 1