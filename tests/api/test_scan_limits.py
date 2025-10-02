# tests/api/test_scan_limits.py
def test_scan_limits_header(client, monkeypatch):
    # 透過 header 設定 symbols 限額
    body = {
        "strategy_id": 1,
        "symbols": ["2330", "2317"],
        "timeframe": "1D",
        "ts": "2025-09-28 00:00:00",
        "signal_type": "buy",
        "strength": 0.6,
    }
    r = client.post(
        "/api/v1/scan/run-now",
        json=body,                               # ← 改成 json=body
        headers={"X-Scan-Symbols-Limit": "1"},   # ← header 留著
    )
    assert r.status_code == 413
    j = r.json()
    assert j["detail"]["error_code"] == "PAYLOAD_TOO_LARGE"
    assert j["detail"]["limit"] == 1
    assert j["detail"]["got"] == 2