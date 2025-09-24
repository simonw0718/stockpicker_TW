# Phase 1A 完成報告（可封版）

## 範圍與成果
- 策略 JSON 表示法（最小子集）
- Level 2 驗證（欄位完整性 + 參數域值 + `MACD.fast < slow` + 交叉不接受 Number）
- 錯誤格式統一（`path` / `code` / `message`），並過濾 Union 噪音
- 驗證工具：`tools/validate_strategy.py`
- JSON Schema：`src/app/resources/schemas/strategy.schema.json`

## 主要產物
- `src/app/domain/strategies/validation.py`
- `src/app/resources/schemas/strategy.schema.json`
- `docs/strategies/representation.md`
- `docs/api/errors.md`
- `docs/api/strategies.md`
- `tests/resources/strategies/test_samples.json`
- `tests/resources/strategies/expected_report.json`

## 驗收結果（摘要）
- 成功樣例：200 ✅
- 失敗樣例1（非法運算子）：422，`invalid_enum`
- 失敗樣例2（參數越界 + 關係不成立）：422，`out_of_range` & `invalid_relation`

## 待辦（交接至 1C）
- 實作 `/strategies` CRUD + `/strategies/validate`
- 409/404 測試
- Level 3 驗證（cross_* 型別/對齊、欄位相容性等）