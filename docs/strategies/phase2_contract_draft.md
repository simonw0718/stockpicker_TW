# Phase 2 — MVP 契約草案彙整

## 1. 掃描器契約（scan_runner）

- **Input**
  - `strategy_id` (uuid)
  - `symbols` (array<string>) — MVP 可多個，但回測先支援單一 symbol
  - `start_date`, `end_date` (date)
  - `timeframe` = `1D` (MVP)
  - `params_snapshot` (jsonb) — 通過 Phase1 的 `params_schema`
- **Output**
  - `signals`（存入 DB）
    - `ts` (timestamptz, +08:00)
    - `symbol` (text)
    - `strategy_id` (uuid)
    - `strategy_version` (int)
    - `params_hash` (char(64))
    - `score` (0~1, 連續值)
    - `features` (jsonb, 指標快照)
    - `source` = `scan`
    - `created_at` (timestamptz)
- **Input範例**
  ```json
  {
    "strategy_id": "b6f9d9b4-0b0f-4e21-84a5-4e3c2a9a12ab",
    "symbols": ["TSM", "AAPL"],
    "start_date": "2025-09-01",
    "end_date": "2025-09-26",
    "timeframe": "1D",
    "params_snapshot": { "ma_fast": 20, "ma_slow": 60 }
  }
  ```
- **Output範例**
  ```json
  {
    "signal_id": "7e4f7a35-0c9a-4b5f-9b3e-12d4e5f6a7b8",
    "ts": "2025-09-25T16:30:00+08:00",
    "symbol": "TSM",
    "strategy_id": "b6f9...",
    "strategy_version": 3,
    "params_hash": "9f3e...a1c4",
    "score": 0.91,
    "features": { "breakout_pct": 0.034, "vol_ratio": 1.6 },
    "source": "scan",
    "created_at": "2025-09-25T16:30:02+08:00"
  }
  ```
- **其他規則**
  - timeframe：先日線，weekly/monthly/hours 後續擴充
  - 價格序列：**前復權（含息含拆）**
  - 記錄 `strategy_version`, `params_hash`
  - 去重：`(strategy_id, strategy_version, symbol, ts)` 唯一
  - 衝突行為：**UPSERT 更新**

---

## 2. 回測契約（backtest_runner）

- **Input**
  ```json
  {
    "strategy_id": "b6f9d9b4-0b0f-4e21-84a5-4e3c2a9a12ab",
    "symbol": "TSM",
    "timeframe": "1D",
    "start_date": "2018-01-01",
    "end_date": "2024-12-31",
    "params_snapshot": { "ma_fast": 20, "ma_slow": 60 },
    "price_adjustment": "adjusted",
    "assumptions": {
      "exec": "T+1_open",
      "fees": 0,
      "slippage": 0,
      "sizing_rule": "fixed",
      "sizing_params": {},
      "exit_overrides": { "stop_loss_pct": null, "take_profit_pct": null, "max_holding_days": null }
    }
  }
  ```
- **Output**
  ```json
  {
    "run_id": "f3c0a8f8-3d3f-4a1f-9f0a-6a8b1caa4e40",
    "status": "done",
    "metrics_summary": { "win_rate": 0.51, "total_pnl": 18234.7, "max_drawdown": -0.09, "CAGR": 0.21, "Sharpe": 1.35 },
    "links": {
      "trades": "/api/v1/backtest/f3c0a8f8-3d3f-4a1f-9f0a-6a8b1caa4e40/trades",
      "equity_curve": "/api/v1/backtest/f3c0a8f8-3d3f-4a1f-9f0a-6a8b1caa4e40/equity-curve"
    }
  }
  ```
- **規則**
  - 出場：MVP 為 **反向訊號全平**，契約預留 exit 欄位
  - 資金管理：MVP 固定 1 單位，契約預留 `sizing_rule`, `sizing_params`
  - 防呆：避免 look-ahead bias；warmup 視窗依策略最大期間

---

## 3. DB Schema（MVP）

### `backtest_runs` 範例
```json
{
  "run_id": "f3c0a8f8-3d3f-4a1f-9f0a-6a8b1caa4e40",
  "strategy_id": "b6f9...",
  "strategy_version": 3,
  "params_hash": "9f3e...a1c4",
  "params_snapshot": { "ma_fast": 20, "ma_slow": 60 },
  "symbol": "TSM",
  "timeframe": "1D",
  "price_adjustment": "adjusted",
  "start_date": "2018-01-01",
  "end_date": "2024-12-31",
  "metrics_summary": { "win_rate": 0.51, "total_pnl": 18234.7, "max_drawdown": -0.09, "CAGR": 0.21, "Sharpe": 1.35 },
  "status": "done",
  "created_at": "2025-09-26T16:35:00+08:00",
  "finished_at": "2025-09-26T16:36:15+08:00"
}
```

### `trades` 範例
```json
{
  "trade_id": "c2a9f6a1-0b5f-4d6c-8a1e-0b5f6a1c2d3e",
  "run_id": "f3c0a8f8-3d3f-4a1f-9f0a-6a8b1caa4e40",
  "symbol": "TSM",
  "side": "long",
  "qty": 1,
  "entry_ts": "2023-05-02T09:00:00+08:00",
  "entry_px": 520.5,
  "exit_ts": "2023-06-10T09:00:00+08:00",
  "exit_px": 548.0,
  "exit_reason": "reverse_signal",
  "pnl": 27.5,
  "pnl_pct": 0.0528,
  "holding_days": 39
}
```

### `signals` 範例
```json
{
  "signal_id": "7e4f7a35-0c9a-4b5f-9b3e-12d4e5f6a7b8",
  "ts": "2025-09-25T16:30:00+08:00",
  "symbol": "TSM",
  "strategy_id": "b6f9...",
  "strategy_version": 3,
  "params_hash": "9f3e...a1c4",
  "score": 0.91,
  "features": { "breakout_pct": 0.034 },
  "source": "scan",
  "run_id": null,
  "created_at": "2025-09-25T16:30:02+08:00"
}
- **唯一鍵**：(strategy_id, strategy_version, symbol, ts)
- **衝突處理**：UPSERT 更新
```

### `alerts` 範例
```json
{
  "alert_id": "a1b2c3d4-e5f6-7890-ab12-c3d4e5f67890",
  "signal_id": "7e4f7a35-0c9a-4b5f-9b3e-12d4e5f6a7b8",
  "ts": "2025-09-25T16:30:00+08:00",
  "strategy_id": "b6f9...",
  "symbol": "TSM",
  "payload": { "symbol": "TSM", "ts": "2025-09-25T16:30:00+08:00", "strategy_id": "b6f9...", "score": 0.91 },
  "webhook_status": "pending",
  "attempts": 0,
  "last_error": null,
  "created_at": "2025-09-25T16:30:03+08:00"
}
```

---

## 4. API 契約（草案）


### `/backtest`
- **POST /backtest**
  - 建立單一 symbol 回測
  - 驗證：timeframe=1D, 日期合法, strategy 存在且 active, params 驗證
  - 回傳 run_id 與 status=pending
- **GET /backtest/{run_id}**
  - 查 run 摘要與 metrics
  - links: trades, equity_curve
- **GET /backtest/{run_id}/trades**
  - 查交易明細，分頁與排序

### `/scan`
- **POST /scan**
  - 提交批次掃描（symbols ≤500）
  - 回傳 job_id 與 status=pending

### `/signals`
- **GET /signals**
  - 篩選：start_ts/end_ts, symbol, strategy_id, source
  - 分頁：limit=50, offset
  - 排序：order_by=ts|score|symbol，預設 ts desc

### `/alerts`
- **GET /alerts**
  - 篩選：ts 範圍, symbol, strategy_id, webhook_status
  - 分頁與排序
  - payload 格式：`{symbol, ts, strategy_id, score}`

### 共用規則
- **分頁**：limit 50（max 200）, offset
- **排序**：order_by + order
- **錯誤格式**
  ```json
  { "error_code": "VALIDATION_ERROR", "message": "xxx", "details": {"field": "xxx"} }

### 以下為範例 `/backtest`
- **POST /backtest**
  **Request**
  ```json
  {
    "strategy_id": "b6f9...",
    "symbol": "TSM",
    "timeframe": "1D",
    "start_date": "2018-01-01",
    "end_date": "2024-12-31",
    "params_snapshot": { "ma_fast": 20, "ma_slow": 60 },
    "price_adjustment": "adjusted",
    "assumptions": { "exec": "T+1_open", "fees": 0, "slippage": 0, "sizing_rule": "fixed", "sizing_params": {} }
  }
  ```
  **Response**
  ```json
  {
    "run_id": "f3c0a8f8-3d3f-4a1f-9f0a-6a8b1caa4e40",
    "status": "pending",
    "created_at": "2025-09-26T16:35:00+08:00"
  }
  ```

- **GET /backtest/{run_id}**
  **Response**
  ```json
  {
    "run": {
      "run_id": "f3c0...",
      "strategy_id": "b6f9...",
      "symbol": "TSM",
      "timeframe": "1D",
      "metrics_summary": { "win_rate": 0.51, "total_pnl": 18234.7, "max_drawdown": -0.09, "CAGR": 0.21, "Sharpe": 1.35 },
      "status": "done",
      "created_at": "2025-09-26T16:35:00+08:00"
    },
    "links": {
      "trades": "/api/v1/backtest/f3c0.../trades",
      "equity_curve": "/api/v1/backtest/f3c0.../equity-curve"
    }
  }
  ```

- **GET /backtest/{run_id}/trades**
  **Response**
  ```json
  {
    "items": [
      { "trade_id": "...", "side": "long", "qty": 1, "entry_ts": "...", "entry_px": 520.5, "exit_ts": "...", "exit_px": 548.0, "exit_reason": "reverse_signal", "pnl": 27.5, "pnl_pct": 0.0528, "holding_days": 39 }
    ],
    "total": 128,
    "limit": 50,
    "offset": 0
  }
  ```

### `/scan`
- **POST /scan**
  **Request**
  ```json
  { "strategy_id": "b6f9...", "symbols": ["TSM","AAPL"], "start_date": "2025-09-01", "end_date": "2025-09-26", "timeframe": "1D", "params_snapshot": {"ma_fast":20,"ma_slow":60} }
  ```
  **Response**
  ```json
  { "job_id": "af99...", "status": "pending" }
  ```

### `/signals`
- **GET /signals**
  **Response**
  ```json
  {
    "items": [
      { "signal_id": "...", "ts": "2025-09-25T16:30:00+08:00", "symbol": "TSM", "strategy_id": "b6f9...", "score": 0.91, "source": "scan" }
    ],
    "total": 212,
    "limit": 50,
    "offset": 0
  }
  ```

### `/alerts`
- **GET /alerts**
  **Response**
  ```json
  {
    "items": [
      { "alert_id": "...", "signal_id": "...", "ts": "2025-09-25T16:30:00+08:00", "strategy_id": "b6f9...", "symbol": "TSM", "payload": {"symbol":"TSM","ts":"...","+08:00","strategy_id":"b6f9...","score":0.91}, "webhook_status": "sent" }
    ],
    "total": 21,
    "limit": 50,
    "offset": 0
  }
  ```

### 共用規則
- **分頁**：limit 50（max 200）, offset
- **排序**：order_by + order
- **錯誤格式**
  ```json
  { "error_code": "VALIDATION_ERROR", "message": "xxx", "details": {"field": "xxx"} }
  ```
