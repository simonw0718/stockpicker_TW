## Phase 1A — 策略表示法 + JSON Schema 驗證（定稿 v1）

### 0) 範圍與原則
- 範圍：**策略 JSON 表示法（最小子集）** + **JSON Schema 驗證規格（Level 2）**
- 原則：
  - 先解決「欄位完整性 + 參數域值」；跨欄位邏輯（型別/對齊/交叉適用性）延至 Phase1C
  - 所有時間頻率固定 `1d`；warm-up 期間回 `NaN` 屬正常

---

### 1) 策略 JSON 結構（欄位定義）
- `name` (string, required, 3–64)
- `version` (string, required, `major.minor.patch`，例：`0.1.0`)
- `type` (enum, required): `screen` | `backtest`（Phase1 以 `screen` 為主）
- `description` (string, optional, ≤ 200 chars)
- `timeframe` (enum, required): `1d`
- `universe` (object, optional)
  - 例：`{ "watchlist": "tw_top150" }` 或 `{ "symbols": ["2330.TW","2303.TW"] }`
- `logic` (enum, required): `AND` | `OR`
- `conditions` (array<Condition>, required, minItems=1)
- `params` (object, optional)
- `metadata` (object, optional)

**Condition**
- `left`  (Operand, required)
- `op`    (enum, required): `> < >= <= == != cross_up cross_down`
- `right` (Operand, required)
- `note`  (string, optional)

**Operand 型別**
- `Number`: `{ "value": number }`（範圍建議 `[-1e9, 1e9]`）
- `SeriesRef`: `{ "series": "open|high|low|close|volume" }`
- `IndicatorRef`:
  - 必填：`indicator`（見下）、`params`（依指標）
  - 可選：`source`（`close|open|high|low|typical|hlc3`，預設 `close`）
  - 可選：`field`（僅多欄輸出指標）
    - `MACD`: `macd|signal|hist`
    - `BOLL`: `upper|middle|lower`
    - `KD`: `k|d`

---

### 2) 運算子與合法組合
- 頂層布林：`logic ∈ {AND, OR}`
- 比較：`> < >= <= == !=`
  - 左右可為 `Number` / `SeriesRef` / `IndicatorRef`（單欄輸出或指定 `field`）
- 交叉：`cross_up`, `cross_down`
  - 左右**必須**為兩個可對齊的**序列**（`SeriesRef` 或 `IndicatorRef` 單欄輸出）
  - **不接受** `Number`（此規範在 1C 會升級為嚴格檢查）

---

### 3) 指標參數域值（Level 2 驗證基準）
- `MA`：`window ∈ [2, 400]`，`source?`
- `EMA`：`window ∈ [2, 400]`，`source?`
- `RSI`：`period ∈ [2, 250]`，`source?`
- `MACD`：`fast ∈ [2, 400]`，`slow ∈ [2, 400]`，`signal ∈ [2, 200]`，且 **`fast < slow`**；`source?`；`field ∈ {macd,signal,hist}`
- `BOLL`：`window ∈ [5, 400]`，`mult ∈ [0.5, 5]`；`source?`；`field ∈ {upper,middle,lower}`
- `KD`：`k_period ∈ [2, 200]`，`d_period ∈ [2, 200]`，`smooth ∈ [1, 20]`；`field ∈ {k,d}`
- `BIAS`：`window ∈ [2, 400]`，`source?`
- `VOLUME`：可無參數；可選 `window ∈ [2, 400]` 產生均量
- `DIFF`（價差）：
  - 內部來源需合法（`open|high|low|close` 或 `indicator(field)`）
  - 引用其他指標時，其參數需各自通過上述域值

**共同規範**
- 整數參數需為正整數；浮點需為有限數
- 缺參數或超出域值 → 422

---

### 4) JSON Schema 驗證（文字版規格）
- **必要欄位**：`name, version, type, timeframe, logic, conditions`
- **型別**：`string/array/object/number` 嚴格檢查；`conditions` 至少 1 條
- **枚舉**：`type{screen,backtest}`、`timeframe{1d}`、`logic{AND,OR}`、`op{>,<,>=,<=,==,!=,cross_up,cross_down}`
- **Operand 驗證**：
  - `Number`：僅允許 `value`
  - `SeriesRef`：僅允許 `series ∈ {open,high,low,close,volume}`
  - `IndicatorRef`：必含 `indicator` 與 `params`；若指標多欄輸出需 `field`
- **參數域值**：依 §3；`MACD.fast < slow` 屬 Level 2（當場擋）
- **交叉提示**：`cross_*` 不接受 `Number`（Phase1A 層級屬規格提示；實作擋在 1C）

---

### 5) 成功/失敗範例（審核用 JSON 樣例）
(與之前相同)
