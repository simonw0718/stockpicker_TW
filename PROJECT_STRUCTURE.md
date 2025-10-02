.
├── .DS_Store
├── .github
│   └── workflows
│       └── ci.yml
├── .gitignore
├── .pytest_cache
│   ├── .gitignore
│   ├── CACHEDIR.TAG
│   ├── README.md
│   └── v
│       └── cache
│           ├── lastfailed
│           └── nodeids
├── .vscode
│   └── settings.json 
├── conftest.py
├── data
│   ├── app.db
│   ├── duckdb
│   └── parquet
├── docs
│   ├── _backup
│   │   └── 20250925-110908-strategies.py
│   ├── .DS_Store
│   ├── api
│   │   ├── errors.md
│   │   └── strategies.md
│   └── strategies
│       ├── phase1a_report.md
│       ├── phase1b_report.md
│       ├── phase1c_report.md
│       ├── representation.md
│       └── schema_readme.md
├── Makefile
├── PROJECT_STRUCTURE.md
├── pyrightconfig.json
├── pytest.ini
├── README.md
├── requirements.lock
├── requirements.txt
├── src
│   ├── __init__.py
│   └── app
│       ├── __init__.py
│       ├── db
│       │   ├── __init__.py
│       │   ├── conn.py
│       │   ├── migrate_v2.py
│       │   └── schema_v2.sql
│       ├── domain
│       │   ├── __init__.py
│       │   └── strategies
│       │       ├── __init__.py
│       │       └── validation.py
│       ├── indicators
│       │   ├── __init__.py
│       │   ├── base.py
│       │   ├── builtin
│       │   │   ├── bias.py
│       │   │   ├── boll.py
│       │   │   ├── diff.py
│       │   │   ├── ema.py
│       │   │   ├── ma.py
│       │   │   ├── macd.py
│       │   │   ├── rsi.py
│       │   │   └── volume.py
│       │   └── registry.py
│       ├── main.py
│       ├── models
│       │   ├── __init__.py
│       │   └── watchlists.py
│       ├── repositories
│       │   ├── __init__.py
│       │   └── strategies.py
│       ├── resources
│       │   └── schemas
│       │       └── strategy.schema.json
│       ├── routers
│       │   ├── __init__.py
│       │   ├── alerts.py
│       │   ├── strategies.py
│       │   ├── symbols.py
│       │   └── watchlist.py
│       ├── runners
│       │   ├── __init__.py
│       │   ├── alert_runner.py
│       │   ├── backtest_runner.py
│       │   ├── init.py
│       │   └── scan_runner.py
│       └── services
│           ├── __init__.py
│           ├── data_pipeline
│           │   ├── __init__.py
│           │   ├── duckdb_io.py
│           │   └── yahoo_ingest.py
│           └── resolve.py
├── tests
│   ├── __init__.py
│   ├── api
│   │   └── test_strategies.py
│   ├── conftest.py
│   ├── domain
│   │   └── indicators
│   │       └── test_contract.py
│   ├── resources
│   │   ├── __init__.py
│   │   └── strategies
│   │       ├── __init__.py
│   │       ├── expected_report.json
│   │       ├── test_samples.json
│   │       └── test_samples.py
│   ├── test_health.py
│   ├── test_runners_contracts.py
│   ├── test_schema_v2.py
│   ├── test_symbols.py
│   └── test_watchlist.py
├── tools
│   └── validate_strategy.py
└── validation_report.json

36 directories, 84 files
