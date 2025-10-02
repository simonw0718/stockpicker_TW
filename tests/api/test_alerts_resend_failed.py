from fastapi.testclient import TestClient
from app.main import app
from app.db.conn import get_conn

client = TestClient(app)

def _seed_failed_alert():
    conn = get_conn()
    conn.execute("""
        INSERT INTO alerts(symbol, condition, timeframe, status, last_triggered_ts, channel, attempts, last_error, created_at, updated_at)
        VALUES('2330','strategy:1:buy','1D','failed','2025-09-29 00:00:00','webhook',2,'webhook 500',datetime('now'),datetime('now'))
    """)
    conn.commit()

def test_resend_failed():
    _seed_failed_alert()
    r = client.post("/api/v1/alerts/resend-failed", params={"limit": 10})
    assert r.status_code == 200
    j = r.json()
    assert j["resend"] >= 1

    # 查詢應無 failed（或數量下降）
    r2 = client.get("/api/v1/alerts?webhook_status=failed&limit=1")
    assert r2.status_code == 200
    assert r2.json()["total"] == 0