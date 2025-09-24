# tests/test_runners_contracts.py
from backend.app.runners import scan_runner, backtest_runner, alert_runner

def test_scan_runner_contract():
    results = scan_runner.run_scan(["2330", "2454"])
    assert isinstance(results, list)
    assert "symbol" in results[0]
    assert "signal_type" in results[0]

def test_backtest_runner_contract():
    result = backtest_runner.run_backtest("demo", {}, ["2330"], ("2020-01-01", "2021-01-01"))
    assert "run_id" in result
    assert "metrics" in result
    assert result["status"] in ["queued", "done"]

def test_alert_runner_contract():
    results = alert_runner.evaluate_alerts("2025-01-01T00:00:00Z")
    assert isinstance(results, list)