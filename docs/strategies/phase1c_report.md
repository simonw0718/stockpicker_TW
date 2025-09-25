# Phase 1C Report — Strategies API + DB

## 目標
完成 **Strategies API + DB 契約**，將 Phase 1A 的驗證邏輯串接至資料庫層，並實現完整 CRUD 與邏輯刪除。

---

## 完成項目

### 資料庫應用
- 使用 `strategies` / `params` 表（來自 Phase0 / schema_v2.sql）。
- 新增策略時，保存完整 JSON/DSL 至 `strategies.payload`。
- `params` 表存放快照（若存在）。
- 支援 versioning 與 description 欄位。
- 刪除：以 `deleted_at` 標記軟刪，保留追溯性。

### API 行為
- **POST** `/api/v1/strategies/validate`  
  Schema 驗證成功 → `200 {"ok": true}`
- **POST** `/api/v1/strategies`  
  新增成功 → `201 {id, name, version}`  
  衝突（同名同版未刪除）→ `409`
- **GET** `/api/v1/strategies/{id}`  
  成功 → `200 {...}`  
  已刪除 / 不存在 → `404`
- **PUT** `/api/v1/strategies/{id}`  
  更新成功 → `200 {...}`  
  衝突 → `409`
- **DELETE** `/api/v1/strategies/{id}`  
  軟刪 → `204`
- **POST** `/api/v1/strategies/{id}/validate`  
  重跑 Schema 驗證，stub 回 `{"ok": true}`。

### 錯誤碼對齊
- 422 Schema 驗證錯誤（`format_validation_error`）
- 409 衝突（name+version 已存在）
- 404 not_found（找不到或已刪除）

---

## 測試驗收

- **pytest 全套**：`22 passed`  
- **Smoke 測試**：
  - Create → 201  
  - Conflict → 409  
  - Get → 200  
  - Update → 200  
  - Validate existing → 200  
  - Delete → 204  
  - Get after delete → 404  

驗證流程完整覆蓋，與 Phase 1A 契約對齊。

---

## 驗收標準對照

- [x] `/strategies/validate` 成功樣例  
- [x] `/strategies` Create/Update 串接驗證  
- [x] 422 回傳符合格式  
- [x] 成功案例存 DB  
- [x] 409 / 404 行為符合預期  
- [x] CI 綠燈  

---

## 結論
Phase 1C 已完成，Strategies API 與資料庫契約正式收斂。  
下一階段（Phase 2）可將重點轉至 **執行引擎 / 回測模組**，與策略契約進一步整合。
