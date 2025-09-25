# tests/api/test_strategies_smoke.py
import json
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def _ok_strategy():
    from tests.resources.strategies.test_samples import load
    data = json.loads(open("tests/resources/strategies/test_samples.json").read())
    return data["success_samples"][0]

def test_create_get_delete_flow():
    s = _ok_strategy()
    # Create
    r = client.post("/api/v1/strategies", json={"strategy": s})
    assert r.status_code == 201, r.text
    sid = r.json()["id"]

    # Read by id
    r = client.get(f"/api/v1/strategies/{sid}")
    assert r.status_code == 200
    assert r.json()["name"] == s["name"]

    # Conflict on create same name+version
    r2 = client.post("/api/v1/strategies", json={"strategy": s})
    assert r2.status_code == 409

    # Validate existing
    r = client.post(f"/api/v1/strategies/{sid}/validate")
    assert r.status_code == 200 and r.json()["ok"] is True

    # Delete
    r = client.delete(f"/api/v1/strategies/{sid}")
    assert r.status_code == 204

    # 404 after delete
    r = client.get(f"/api/v1/strategies/{sid}")
    assert r.status_code == 404