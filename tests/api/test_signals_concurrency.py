# tests/api/test_signals_concurrency.py
from concurrent.futures import ThreadPoolExecutor, as_completed

def test_signals_upsert_concurrency(client):
    body = {
        "strategy_id": 1,
        "symbol": "2330",
        "ts": "2025-09-28 00:00:00",
        "timeframe": "1D",
        "signal_type": "buy",
        "strength": 0.8,
    }

    def call():
        return client.post("/api/v1/signals/upsert", json=body)  # ← 修正

    futures = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        for _ in range(16):
            futures.append(ex.submit(call))
        codes = [f.result().status_code for f in as_completed(futures)]
    assert all(c in (200, 201) for c in codes)

    r = client.get(
        "/api/v1/signals?symbol=2330&timeframe=1D&order_by=ts&order=desc&limit=10"
    )
    assert r.status_code == 200
    js = r.json()
    rows = [it for it in js["items"] if it["ts"] == "2025-09-28 00:00:00"]
    assert len(rows) == 1