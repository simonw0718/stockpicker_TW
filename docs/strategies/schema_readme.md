
# Phase1A — Schema Implementation (Step 1)

This folder contains:
- `strategy_schema.py`: Pydantic models implementing the **Level 2** validation rules, including ranges and `MACD.fast < slow`, and `cross_*` operator constraint (no Number operands).
- `validate_samples.py`: Helper to validate sample payloads and print a report (JSON) to stdout.
- `strategy.schema.json`: JSON Schema (Draft 2020-12) covering structure and parameter ranges. The cross-parameter constraint `fast < slow` is enforced by the Pydantic validator (standard JSON Schema cannot compare sibling values portably).

## How to use

### 1) Install dependencies
```bash
pip install pydantic==1.*
```

### 2) Validate sample payloads
```bash
python validate_samples.py ../Phase1A_Test_Samples.json > validation_report.json
```

The output will include entries for each sample with either:
- `{"status": 200, "ok": true}` on success
- or a `422`-style error object with `path`, `code`, and `message` fields.

### 3) Integrate into `/strategies` Create/Update
- Import `Strategy` and call `Strategy.parse_obj(payload)` before persisting.
- On `ValidationError`, transform errors using `format_validation_error()` and return `422` with that JSON body.

## Notes
- Timeframe is fixed to `1d` per Phase 1A scope.
- `cross_*` operators require two series-like operands (no `Number`). Deeper type/alignment checks are deferred to Phase 1C.
