# tests/api/test_scan_stub.py

def test_scan_run_now_inserts_signals(client):
    body = {
        "strategy_id": 1,
        "symbols": ["2330", "2317"],
        "timeframe": "1D",
        "ts": "2025-09-28 00:00:00",
        "signal_type": "buy",
        "strength": 0.6,
    }
    r = client.post("/api/v1/scan/run-now", json=body)
    assert r.status_code == 200
    out = r.json()
    assert out["inserted_signals"] == 2

    # 查 signals（按 ts desc）
    r2 = client.get("/api/v1/signals?order_by=ts&order=desc&limit=5")
    assert r2.status_code == 200
    js = r2.json()
    # 至少包含我們剛剛的兩檔
    syms = {item["symbol"] for item in js["items"]}
    assert {"2330", "2317"} <= syms


def test_scan_run_now_auto_alerts(client):
    body = {
        "strategy_id": 1,
        "symbols": ["2330"],
        "timeframe": "1D",
        "ts": "2025-09-29 00:00:00",
        "signal_type": "buy",
        "strength": 0.7,
        "auto_alert": True,
    }
    r = client.post("/api/v1/scan/run-now", json=body)
    assert r.status_code == 200
    out = r.json()
    assert out["created_alerts"] == 1

    # 查 alerts（ts desc）
    r2 = client.get("/api/v1/alerts?symbol=2330&order_by=ts&order=desc&limit=3")
    assert r2.status_code == 200
    js = r2.json()
    assert js["total"] >= 1
    first = js["items"][0]
    assert first["symbol"] == "2330"
    assert first["status"] in ("pending", "sent", "failed")  # 目前應為 pending