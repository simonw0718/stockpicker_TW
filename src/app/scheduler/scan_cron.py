# src/app/scheduler/scan_cron.py
from __future__ import annotations
from datetime import datetime, timedelta
from typing import Callable, Optional

# 之後可換成 zoneinfo.ZoneInfo("Asia/Taipei")
TZ: Optional[object] = None  # 測試中用 naive datetime；預留介面

class DailyState:
    """記錄每日是否已觸發"""
    def __init__(self) -> None:
        self.last_run_date: Optional[str] = None  # "YYYY-MM-DD"

def next_due(now: datetime) -> datetime:
    """
    計算下一次觸發時間（平日 16:30）。
    若當下已過 16:30 或是假日，往後推到下一個平日的 16:30。
    """
    nxt = now.replace(hour=16, minute=30, second=0, microsecond=0)
    # 今日過了 16:30 → 推一天
    if now >= nxt:
        nxt = nxt + timedelta(days=1)
    # 若是週末則推到下個週一
    while nxt.weekday() >= 5:
        nxt = nxt + timedelta(days=1)
    return nxt

def run_if_due(cb: Callable[[], None], *, state: DailyState, now: datetime) -> bool:
    """
    到期且當日尚未執行 → 呼叫 cb 並回 True；否則 False。
    規則：平日 >= 16:30 才到期；每日僅一次。
    """
    if now.weekday() >= 5:
        return False
    due = (now.hour > 16) or (now.hour == 16 and now.minute >= 30)
    if not due:
        return False
    today = now.strftime("%Y-%m-%d")
    if state.last_run_date == today:
        return False
    cb()
    state.last_run_date = today
    return True