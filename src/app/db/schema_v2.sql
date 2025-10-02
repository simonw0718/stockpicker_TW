-- src/app/db/schema_v2.sql
-- Dialect: SQLite
-- Phase 2 schema（含 Idempotency 與 scan_jobs）

PRAGMA foreign_keys = ON;

-- strategies ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS strategies (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    type TEXT,
    description TEXT,
    payload TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TEXT,
    updated_at TEXT,
    deleted_at TEXT DEFAULT NULL,
    UNIQUE(name, version)
);

-- 單筆 params 快照（每個 strategy 一筆）
CREATE TABLE IF NOT EXISTS params (
    id INTEGER PRIMARY KEY,
    strategy_id INTEGER UNIQUE,
    params_json TEXT,
    created_at TEXT,
    updated_at TEXT,
    FOREIGN KEY(strategy_id) REFERENCES strategies(id) ON DELETE CASCADE
);

-- signals ------------------------------------------------------------------
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

CREATE INDEX IF NOT EXISTS idx_signals_ts_desc       ON signals(ts DESC);
CREATE INDEX IF NOT EXISTS idx_signals_strategy_ts   ON signals(strategy_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_signals_symbol_ts     ON signals(symbol, ts DESC);
CREATE INDEX IF NOT EXISTS idx_signals_strength_desc ON signals(strength DESC);
-- ★ 保障唯一鍵（避免高併發重複）：(strategy_id, symbol, timeframe, ts)
CREATE UNIQUE INDEX IF NOT EXISTS ux_signals_key
  ON signals(strategy_id, symbol, timeframe, ts);

-- backtest_runs（加入 idempotency_key） -----------------------------------
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
    idempotency_key TEXT UNIQUE,
    FOREIGN KEY(strategy_id) REFERENCES strategies(id),
    FOREIGN KEY(param_set_id) REFERENCES params(id)
);

CREATE INDEX IF NOT EXISTS idx_backtests_strategy_created ON backtest_runs(strategy_id, created_at);
CREATE INDEX IF NOT EXISTS idx_backtests_symbol_created   ON backtest_runs(symbol_universe, created_at);
CREATE INDEX IF NOT EXISTS idx_backtests_status           ON backtest_runs(status);

-- trades -------------------------------------------------------------------
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

CREATE INDEX IF NOT EXISTS idx_trades_run          ON trades(run_id);
CREATE INDEX IF NOT EXISTS idx_trades_symbol_entry ON trades(symbol, entry_ts);
CREATE INDEX IF NOT EXISTS idx_trades_exit_ts      ON trades(exit_ts);

-- alerts（維持 Phase0 欄位，補 attempts/last_error/last_sent_ts） ----------
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY,
    symbol TEXT,
    condition TEXT,
    timeframe TEXT,
    status TEXT,
    last_triggered_ts TEXT,
    channel TEXT,
    attempts INTEGER DEFAULT 0,
    last_error TEXT,
    last_sent_ts TEXT,
    created_at TEXT,
    updated_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_alerts_status    ON alerts(status);
CREATE INDEX IF NOT EXISTS idx_alerts_symbol_ts ON alerts(symbol, last_triggered_ts);

-- watchlist ----------------------------------------------------------------
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

-- idempotency for /scan ----------------------------------------------------
CREATE TABLE IF NOT EXISTS scan_jobs (
    key TEXT PRIMARY KEY,
    job_id TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- 兼容舊遺留
DROP TABLE IF EXISTS lists;