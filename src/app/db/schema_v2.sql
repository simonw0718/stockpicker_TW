-- schema_v2: 應用層與回測產物表

CREATE TABLE IF NOT EXISTS strategies (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    version TEXT,
    type TEXT,
    description TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TEXT,
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS params (
    id INTEGER PRIMARY KEY,
    strategy_id INTEGER,
    key TEXT,
    value TEXT,
    scope TEXT,
    created_at TEXT,
    updated_at TEXT,
    UNIQUE(strategy_id, key, scope),
    FOREIGN KEY(strategy_id) REFERENCES strategies(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS signals (
    id INTEGER PRIMARY KEY,
    strategy_id INTEGER,
    symbol TEXT,
    timeframe TEXT,
    signal_type TEXT,
    strength REAL,
    ts TEXT,
    meta TEXT,
    created_at TEXT,
    FOREIGN KEY(strategy_id) REFERENCES strategies(id)
);

CREATE TABLE IF NOT EXISTS backtest_runs (
    id INTEGER PRIMARY KEY,
    strategy_id INTEGER,
    param_set_id INTEGER,
    symbol_universe TEXT,
    date_start TEXT,
    date_end TEXT,
    timeframe TEXT,
    status TEXT,
    metrics TEXT,
    created_at TEXT,
    finished_at TEXT,
    notes TEXT,
    FOREIGN KEY(strategy_id) REFERENCES strategies(id),
    FOREIGN KEY(param_set_id) REFERENCES params(id)
);

CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY,
    run_id INTEGER,
    symbol TEXT,
    side TEXT,
    entry_ts TEXT,
    entry_price REAL,
    exit_ts TEXT,
    exit_price REAL,
    size REAL,
    pnl REAL,
    pnl_pct REAL,
    mae REAL,
    mfe REAL,
    tags TEXT,
    notes TEXT,
    FOREIGN KEY(run_id) REFERENCES backtest_runs(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY,
    symbol TEXT,
    condition TEXT,
    timeframe TEXT,
    status TEXT,
    last_triggered_ts TEXT,
    channel TEXT,
    created_at TEXT,
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS watchlist (
    id INTEGER PRIMARY KEY,
    name TEXT,
    owner TEXT,
    meta TEXT,
    created_at TEXT,
    updated_at TEXT
);

CREATE TABLE IF NOT EXISTS watchlist_items (
    id INTEGER PRIMARY KEY,
    watchlist_id INTEGER,
    symbol TEXT,
    position INTEGER,
    created_at TEXT,
    updated_at TEXT,
    UNIQUE(watchlist_id, symbol),
    FOREIGN KEY(watchlist_id) REFERENCES watchlist(id) ON DELETE CASCADE
);


DROP TABLE IF EXISTS lists;