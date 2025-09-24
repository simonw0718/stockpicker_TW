# Phase 1B 完成報告（初始指標庫設計）

## 🎯 目標
- 建立統一的指標計算介面與註冊機制。
- 先支援日線 (`timeframe="1d"`)。
- 指標清單：MA, EMA, RSI, MACD, 成交量(VOLUME), 價差(DIFF)。
- 預留：布林帶(BOLL), KD, 乖離率(BIAS)。
- 與 Phase 1A 驗證規則一致（參數域值、field/default_field）。

---

## ✅ 完成的產物
- **介面設計**
  - 對外：`calc(indicator, data, params, *, timeframe="1d", field=None) -> pd.Series`
  - 註冊：`registry.register(name, fn, meta)`
- **內建指標**
  - 單欄：MA, EMA, RSI, BIAS, VOLUME, DIFF
  - 多欄：MACD (`macd/signal/hist`), BOLL (`upper/middle/lower`)
- **warm-up/NaN 規則**
  - 依 `window/period` 決定前置 NaN 筆數，pytest 驗證通過。

---

## 🧪 測試結果
- 路徑：`tests/domain/indicators/test_contract.py`
- 測試範圍：未註冊指標、timeframe 限制、缺少欄位、多欄指標 field 行為、warm-up NaN。
- 執行環境：macOS / Python 3.13.7 / venv
- 最終結果：11 passed in 0.47s
- 測試紀錄：
- [T13] `test_ma_warmup` 初版 MA 實作錯誤 → 修正 rolling/warm-up → 通過
- [T14] pytest 全數綠燈（11 passed）

---

## 📂 檔案清單
- `src/app/indicators/base.py` — 型別定義
- `src/app/indicators/registry.py` — 註冊中心 + `calc()`
- `src/app/indicators/__init__.py` — 內建指標註冊
- `src/app/indicators/builtin/*.py` — 各指標實作
- `tests/domain/indicators/test_contract.py` — I/O 合約測試

---

## 🔚 收斂
- **1B 任務完成**：指標庫已具備可用雛形，並與 1A 驗證規格完全對齊。
- **交棒至 1C**：
- `/strategies/validate` 與 CRUD 接口，將驗證 (1A) 與計算 (1B) 串起來。
- 需處理 API 層的 422/409/404 行為。