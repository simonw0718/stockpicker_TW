from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def _assert_ok(resp):
    # 端點可能回 200（OK）或 201（Created），兩者皆接受
    assert resp.status_code in (200, 201), f"unexpected status: {resp.status_code}, body={resp.text}"

def test_signals_unique_upsert():
    # 第一次 upsert（insert）
    r1 = client.post(
        "/api/v1/signals/upsert",
        json={
            "strategy_id": 1,
            "symbol": "2330",
            "ts": "2025-09-28 00:00:00",
            "timeframe": "1D",
            "signal_type": "buy",
            "strength": 0.6,
            "meta": {"seed": 1},
        },
    )
    _assert_ok(r1)
    sid1 = r1.json()["signal_id"]

    # 第二次 upsert 同鍵（update）
    r2 = client.post(
        "/api/v1/signals/upsert",
        json={
            "strategy_id": 1,
            "symbol": "2330",
            "ts": "2025-09-28 00:00:00",
            "timeframe": "1D",
            "signal_type": "buy",
            "strength": 0.9,  # 更新
            "meta": {"seed": 2},
        },
    )
    _assert_ok(r2)
    sid2 = r2.json()["signal_id"]
    assert sid2 == sid1, "同鍵 upsert 應該回同一個 id"

    # 確認只有一筆 & strength 已更新
    r3 = client.get("/api/v1/signals?symbol=2330&strategy_id=1&order_by=ts&order=desc&limit=10")
    assert r3.status_code == 200
    data = r3.json()
    assert data["total"] == 1
    item = data["items"][0]
    assert item["signal_id"] == sid1
    assert abs(item["strength"] - 0.9) < 1e-9