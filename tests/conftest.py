# tests/conftest.py
import pytest
from fastapi.testclient import TestClient

from src.app.main import app
from src.app.db import migrate_v2

@pytest.fixture(autouse=True, scope="function")
def reset_db():
    """
    每個測試函式前都重建乾淨的 data/app.db。
    確保不會殘留舊資料，避免 UNIQUE/position/ghost rows 問題。
    """
    migrate_v2.init_db()
    yield

@pytest.fixture()
def client() -> TestClient:
    """
    提供 FastAPI 測試用 client。
    reset_db fixture 會確保 DB 乾淨。
    """
    return TestClient(app)