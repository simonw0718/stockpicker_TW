from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_backtest_complete_stub_flow():
    # 建 run
    r = client.post("/api/v1/backtest", headers={"Idempotency-Key":"bt-test-1"}, json={
        "strategy_id":1, "symbol":"2330", "timeframe":"1D",
        "start_date":"2020-01-01", "end_date":"2020-12-31", "params_snapshot":{}
    })
    assert r.status_code in (200,201)
    run_id = r.json()["run_id"]

    # 完成 stub
    r2 = client.post(f"/api/v1/backtest/{run_id}/complete")
    assert r2.status_code == 200
    assert r2.json()["status"] == "completed_stub"

    # trades 應有至少 1 筆
    r3 = client.get(f"/api/v1/backtest/{run_id}/trades")
    assert r3.status_code == 200
    assert r3.json()["total"] >= 1