import json, sys, os

# ----- ensure src on sys.path -----
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(THIS_DIR, os.pardir))      # project root
SRC_DIR  = os.path.join(ROOT_DIR, "src")
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

from pydantic import ValidationError
from app.domain.strategies.validation import Strategy, format_validation_error  # <- 正確匯入

def validate_payload(payload: dict):
    try:
        Strategy.parse_obj(payload)
        return {"status": 200, "ok": True}
    except ValidationError as e:
        return format_validation_error(e)

def main(samples_path: str):
    with open(samples_path, "r", encoding="utf-8") as f:
        samples = json.load(f)
    report = {"results": []}
    for kind in ("success_samples","failure_samples"):
        for i, sample in enumerate(samples.get(kind, [])):
            result = validate_payload(sample)
            report["results"].append({
                "idx": i,
                "kind": kind,
                "name": sample.get("name"),
                "result": result
            })
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tools/validate_strategy.py tests/resources/strategies/test_samples.json")
        sys.exit(1)
    main(sys.argv[1])
