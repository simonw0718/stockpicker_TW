# tests/api/test_metrics.py
def test_metrics_basic(client):
    # 先種一筆 signal 與 alert（透過既有 API）
    r1 = client.post("/api/v1/signals/upsert", json={
        "strategy_id": 1, "symbol": "2330", "ts": "2025-09-28 00:00:00",
        "timeframe": "1D", "signal_type": "buy", "strength": 0.6
    })
    assert r1.status_code in (200, 201)

    r2 = client.post("/api/v1/alerts/from-signal", json={
        "strategy_id": 1, "symbol": "2330", "ts": "2025-09-28 00:00:00",
        "timeframe": "1D", "signal_type": "buy"
    })
    assert r2.status_code == 200

    # 讀 metrics
    r3 = client.get("/api/v1/metrics")
    assert r3.status_code == 200
    m = r3.json()
    assert "signals_total" in m
    assert "alerts_total" in m
    assert "backtest_runs_total" in m
    assert "trades_total" in m
    assert "alerts_failed" in m
    assert isinstance(m["signals_total"], int)