# tests/api/test_scan_runner_e2e.py
from __future__ import annotations

def test_scan_runner_e2e_to_api(client):
    """
    目標：用 scan_runner 計算訊號，透過 API /signals/upsert 落 DB，最後從 /signals 讀回驗證。
    這個測試不依賴 /scan/run-now 的 stub 行為，因此較貼近「真正計算 → 寫入 → 查詢」的流程。
    """
    # 1) 呼叫 runner 計算
    from app.runners.scan_runner import run_scan
    out = run_scan(["2330"], indicator="ma", timeframe="1D", params={"window": 3})
    assert len(out) == 1
    sig = out[0]
    assert sig["symbol"] == "2330"
    assert sig["signal_type"] in ("buy", "sell", "noop")
    assert 0.0 <= sig.get("strength", 0.0) <= 1.0

    # 2) 透過 API 落庫（確保 httpx 無警告：使用 json=）
    r = client.post(
        "/api/v1/signals/upsert",
        json={
            "strategy_id": 1,
            "symbol": "2330",
            "ts": "2025-09-30 00:00:00",
            "timeframe": "1D",
            "signal_type": sig["signal_type"],
            "strength": sig.get("strength", 0.0),
            "meta": sig.get("meta", {}),
        },
    )
    assert r.status_code in (200, 201)
    sid = r.json().get("signal_id")
    assert isinstance(sid, int) and sid > 0

    # 3) 讀回 signals，確認存在剛寫入的資料
    r2 = client.get("/api/v1/signals?order_by=ts&order=desc&limit=5")
    assert r2.status_code == 200
    items = r2.json()["items"]
    assert any(x["symbol"] == "2330" and x["signal_id"] == sid for x in items)