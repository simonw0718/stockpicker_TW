.
├── .DS_Store
├── .github
│   └── workflows
│       └── ci.yml
├── backend
│   ├── __init__.py
│   ├── .DS_Store
│   ├── app
│   │   ├── __init__.py
│   │   ├── .DS_Store
│   │   ├── main.py
│   │   ├── models
│   │   │   ├── __init__.py
│   │   │   └── watchlists.py
│   │   ├── routers
│   │   │   ├── __init__.py
│   │   │   ├── .DS_Store
│   │   │   ├── alerts.py
│   │   │   ├── strategies.py
│   │   │   ├── symbols.py
│   │   │   └── watchlist.py
│   │   ├── runners
│   │   │   ├── __init__.py
│   │   │   ├── alert_runner.py
│   │   │   ├── backtest_runner.py
│   │   │   └── scan_runner.py
│   │   └── services
│   │       ├── __init__.py
│   │       ├── data_pipeline
│   │       │   ├── __init__.py
│   │       │   ├── duckdb_io.py
│   │       │   └── yahoo_ingest.py
│   │       └── resolve.py
│   └── db
│       ├── conn.py
│       ├── migrate_v2.py
│       └── schema_v2.sql
├── conftest.py
├── data
│   ├── app.db
│   ├── duckdb
│   └── parquet
├── PROJECT_STRUCTURE.md
├── README.md
├── requirements.lock
├── requirements.txt
└── tests
    ├── conftest.py
    ├── test_health.py
    ├── test_runners_contracts.py
    ├── test_schema_v2.py
    ├── test_symbols.py
    └── test_watchlist.py

15 directories, 39 files


## Environment

- Python: Python 3.13.7
- pytest: 8.4.2
- FastAPI: 0.117.1
- Pydantic: 2.11.9
- Git SHA: cf03f93

## Notables
- CI: .github/workflows/ci.yml
- DB Schema: backend/db/schema_v2.sql
- Phase doc: PHASE_0_README.md, Path.md

