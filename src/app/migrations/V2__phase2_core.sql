-- src/app/migrations/V2__phase2_core.sql
-- Phase 2 schema for backtests, trades, signals, alerts and strategies extensions
-- Dialect: PostgreSQL (dev 可用 SQLite 同名欄位，型別以對應者處理)

BEGIN;

-- 1. Tables --------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS backtest_runs (
  run_id UUID PRIMARY KEY,
  strategy_id UUID NOT NULL,
  strategy_version INT NOT NULL,
  params_hash CHAR(64) NOT NULL,
  params_snapshot JSONB NOT NULL,
  symbol TEXT NOT NULL,
  timeframe TEXT NOT NULL DEFAULT '1D',
  price_adjustment TEXT NOT NULL DEFAULT 'adjusted',
  start_date DATE NOT NULL,
  end_date DATE NOT NULL,
  warmup_bars INT DEFAULT 0,
  assumptions JSONB NOT NULL,
  metrics_summary JSONB,
  status TEXT NOT NULL DEFAULT 'pending',
  error_msg TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  finished_at TIMESTAMPTZ,
  -- Idempotency
  idempotency_key TEXT UNIQUE
);

CREATE INDEX IF NOT EXISTS idx_backtest_runs_strategy_created
  ON backtest_runs (strategy_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_backtest_runs_symbol_created
  ON backtest_runs (symbol, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_backtest_runs_status
  ON backtest_runs (status);

CREATE TABLE IF NOT EXISTS trades (
  trade_id UUID PRIMARY KEY,
  run_id UUID NOT NULL,
  symbol TEXT NOT NULL,
  side TEXT NOT NULL, -- long|short
  qty NUMERIC NOT NULL,
  entry_ts TIMESTAMPTZ NOT NULL,
  entry_px NUMERIC NOT NULL,
  exit_ts TIMESTAMPTZ,
  exit_px NUMERIC,
  exit_reason TEXT, -- reverse_signal|stop_loss|take_profit|time_exit
  pnl NUMERIC,
  pnl_pct NUMERIC,
  holding_days INT,
  meta JSONB,
  CONSTRAINT fk_trades_run FOREIGN KEY (run_id) REFERENCES backtest_runs (run_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_trades_run ON trades (run_id);
CREATE INDEX IF NOT EXISTS idx_trades_symbol_entry ON trades (symbol, entry_ts);
CREATE INDEX IF NOT EXISTS idx_trades_exit_reason ON trades (exit_reason);

CREATE TABLE IF NOT EXISTS signals (
  signal_id UUID PRIMARY KEY,
  ts TIMESTAMPTZ NOT NULL,
  symbol TEXT NOT NULL,
  strategy_id UUID NOT NULL,
  strategy_version INT NOT NULL,
  params_hash CHAR(64) NOT NULL,
  score NUMERIC NOT NULL,
  features JSONB,
  source TEXT NOT NULL, -- scan|backtest|realtime
  run_id UUID,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  UNIQUE (strategy_id, strategy_version, symbol, ts)
);

CREATE INDEX IF NOT EXISTS idx_signals_ts ON signals (ts DESC);
CREATE INDEX IF NOT EXISTS idx_signals_strategy_ts ON signals (strategy_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_signals_symbol_ts ON signals (symbol, ts DESC);
CREATE INDEX IF NOT EXISTS idx_signals_score_desc ON signals (score DESC);

CREATE TABLE IF NOT EXISTS alerts (
  alert_id UUID PRIMARY KEY,
  signal_id UUID NOT NULL,
  ts TIMESTAMPTZ NOT NULL,
  strategy_id UUID NOT NULL,
  symbol TEXT NOT NULL,
  payload JSONB NOT NULL,
  webhook_status TEXT NOT NULL DEFAULT 'pending', -- pending|sent|failed|skipped
  attempts INT NOT NULL DEFAULT 0,
  last_error TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT fk_alerts_signal FOREIGN KEY (signal_id) REFERENCES signals (signal_id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_alerts_strategy_ts ON alerts (strategy_id, ts DESC);
CREATE INDEX IF NOT EXISTS idx_alerts_status ON alerts (webhook_status);

-- Idempotency for /scan：用 key 對映 job_id
CREATE TABLE IF NOT EXISTS scan_jobs (
  key TEXT PRIMARY KEY,
  job_id TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 2. Alter strategies ----------------------------------------------------------

ALTER TABLE strategies
  ADD COLUMN IF NOT EXISTS webhook_url TEXT,
  ADD COLUMN IF NOT EXISTS version INT,
  ADD COLUMN IF NOT EXISTS params_schema JSONB;

-- 3. Notes ---------------------------------------------------------------------
-- - 時區一律以 timestamptz 存，外部採 ISO8601(+08:00)。
-- - 價格口徑：adjusted；assumptions 中明列 exec/fees/slippage/sizing/exit_overrides。
-- - signals 唯一鍵衝突 → 以 UPSERT 更新（由應用層使用 ON CONFLICT DO UPDATE 達成）。

COMMIT;