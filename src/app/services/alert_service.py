# alert_service.py
from typing import Dict, Any, Tuple, List

class AlertService:
    def __init__(self, alerts_repo):
        self.alerts = alerts_repo

    def list_alerts(self, db, q: Dict[str, Any]) -> tuple[list[Dict[str, Any]], int]:
        return self.alerts.list_alerts(db, **q)