# tests/api/test_scan_scheduler.py
from datetime import datetime, timedelta
from app.scheduler.scan_cron import DailyState, next_due, run_if_due

def test_next_due_weekday_and_weekend():
    # 週一上午 → 當天 16:30
    mon = datetime(2025, 9, 29, 10, 0)  # <- 移除 tzinfo
    nxt = next_due(mon)
    assert nxt.date() == mon.date()
    assert (nxt.hour, nxt.minute) == (16, 30)

    # 週五傍晚 → 下週一 16:30
    fri = datetime(2025, 9, 26, 17, 0)
    nxt2 = next_due(fri)
    assert nxt2.weekday() == 0
    assert (nxt2.hour, nxt2.minute) == (16, 30)

def test_run_if_due_triggers_once_per_day():
    state = DailyState()
    # 平日 16:31 觸發
    now1 = datetime(2025, 9, 29, 16, 31)
    count = {"n": 0}

    def _cb():
        count["n"] += 1

    assert run_if_due(_cb, state=state, now=now1) is True
    assert count["n"] == 1

    # 同日晚一小時 → 不再觸發
    now2 = now1 + timedelta(hours=1)
    assert run_if_due(_cb, state=state, now=now2) is False
    assert count["n"] == 1

    # 隔天同時間 → 再觸發
    now3 = now1 + timedelta(days=1)
    assert run_if_due(_cb, state=state, now=now3) is True
    assert count["n"] == 2

    # 週六 → 不觸發
    sat = datetime(2025, 9, 27, 16, 40)
    assert run_if_due(_cb, state=state, now=sat) is False