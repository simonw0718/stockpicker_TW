# tests/api/test_idempotency.py
import json
from app.db.conn import get_conn

BT_URL = "/api/v1/backtest"
SCAN_URL = "/api/v1/scan"

def test_backtest_idempotent(client):
    key = "bt-2330-20200101-20201231"
    payload = {
        "strategy_id": 1,
        "symbol": "2330",
        "timeframe": "1D",
        "start_date": "2020-01-01",
        "end_date": "2020-12-31",
        "params_snapshot": {},
    }

    r1 = client.post(BT_URL, headers={"Idempotency-Key": key}, json=payload)
    assert r1.status_code == 200
    run_id_1 = r1.json()["run_id"]

    r2 = client.post(BT_URL, headers={"Idempotency-Key": key}, json=payload)
    assert r2.status_code == 200
    run_id_2 = r2.json()["run_id"]

    assert run_id_1 == run_id_2, "same key should return the same run_id"

    # DB 應只有 1 筆同 key
    conn = get_conn()
    row = conn.execute(
        "SELECT COUNT(*) AS c FROM backtest_runs WHERE idempotency_key = ?",
        (key,),
    ).fetchone()
    assert int(row["c"]) == 1


def test_scan_idempotent(client):
    key = "scan-2330-20200101"
    payload = {
        "strategy_id": 1,
        "symbols": ["2330"],
        "start_date": "2020-01-01",
        "end_date": "2020-12-31",
        "timeframe": "1D",
    }

    r1 = client.post(SCAN_URL, headers={"Idempotency-Key": key}, json=payload)
    assert r1.status_code == 200
    job1 = r1.json()["job_id"]

    r2 = client.post(SCAN_URL, headers={"Idempotency-Key": key}, json=payload)
    assert r2.status_code == 200
    job2 = r2.json()["job_id"]

    assert job1 == job2, "same key should return the same job_id"

    # DB 應只有 1 筆同 key
    conn = get_conn()
    row = conn.execute(
        "SELECT COUNT(*) AS c FROM scan_jobs WHERE key = ?",
        (key,),
    ).fetchone()
    assert int(row["c"]) == 1