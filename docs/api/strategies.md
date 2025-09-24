# Strategies API 契約（Phase 1A 最小雛形）

> 範圍：只定義驗證行為與基本 CRUD 契約；實作允許使用 in-memory repository（不連 DB）。  
> 錯誤格式：對齊 `docs/api/errors.md`。

## 共通
- Media type: `application/json`
- Timeframe：固定 `1d`（Phase1A）
- 策略 JSON 結構：見 `docs/strategies/representation.md`

---

## POST `/strategies/validate`
僅做**格式與參數域值（Level 2）**驗證，**不**持久化。

### Request Body
- `strategy`：策略 JSON

### Responses
- `200 OK`
```json
{ "ok": true }
```

- `422 Unprocessable Entity`
```json
{
  "status": 422,
  "errors": [
    {
      "path": "conditions[0].op",
      "code": "invalid_enum",
      "message": "unexpected value; permitted: '>', '<', '>=', '<=', '==', '!=', 'cross_up', 'cross_down'"
    }
  ]
}
```

---

## POST `/strategies`
建立策略（允許上傳 `name+version` 唯一鍵）。

### Request Body
- `strategy`：策略 JSON

### Responses
- `201 Created`
```json
{ "id": "uuid-or-snowflake", "name": "xxx", "version": "0.1.0" }
```

- `409 Conflict`
```json
{
  "status": 409,
  "error": { "code": "duplicate_name_version", "message": "strategy with name 'xxx' and version '0.1.0' already exists" }
}
```

- `422 Unprocessable Entity`
```json
{
  "status": 422,
  "errors": [ /* 與上方 422 規格相同 */ ]
}
```

---

## GET `/strategies/{id}`

### Responses
- `200 OK`
```json
{ "id": "xxx", "strategy": { /* 策略 JSON 全量 */ }, "deleted_at": null }
```

- `404 Not Found`
```json
{ "status": 404, "error": { "code": "strategy_not_found", "message": "strategy 'xxx' not found or deleted" } }
```

---

## PUT `/strategies/{id}`
以**新版本**更新（建議）：`name` 可不變，但 `version` 需升級。

### Request Body
- `strategy`：策略 JSON

### Responses
- `200 OK`
```json
{ "id": "xxx", "name": "xxx", "version": "0.1.1" }
```
- `409 Conflict`
- `422 Unprocessable Entity`
- `404 Not Found`

---

## DELETE `/strategies/{id}`

### Responses
- `204 No Content`
- `404 Not Found`
