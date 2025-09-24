# Phase 1A — 驗證錯誤訊息格式（草案）

## 422 Unprocessable Entity
```json
{
  "status": 422,
  "errors": [
    {
      "path": "conditions[0].op",
      "code": "invalid_enum",
      "expected": [">","<",">=","<=","==","!=","cross_up","cross_down"],
      "actual": "less_than",
      "message": "op is not in allowed set"
    }
  ]
}
```

## 409 Conflict
```json
{
  "status": 409,
  "error": {
    "code": "duplicate_name_version",
    "message": "strategy with name 'rsi_oversold_ma_cross' and version '0.1.0' already exists"
  }
}
```

## 404 Not Found
```json
{
  "status": 404,
  "error": {
    "code": "strategy_not_found",
    "message": "strategy 'abc' not found or deleted"
  }
}
```
