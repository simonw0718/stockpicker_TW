# tests/conftest.py
import pathlib
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.db import migrate_v2
from app.db.conn import DB_PATH

@pytest.fixture(scope="session", autouse=True)
def _init_db():
    """
    測試前自動建立 data/app.db 並套用 schema_v2。
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    migrate_v2.init_db()
    yield
    # 若不想留下測試資料庫，可在這裡清理：
    # try: DB_PATH.unlink()
    # except FileNotFoundError: pass

@pytest.fixture()
def client() -> TestClient:
    """
    提供 FastAPI 測試用 client。
    """
    return TestClient(app)