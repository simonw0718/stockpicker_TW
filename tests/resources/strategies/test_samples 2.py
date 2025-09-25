import json
from pathlib import Path

def load():
    """Load the JSON test samples that live next to this module."""
    p = Path(__file__).with_name("test_samples.json")
    return json.loads(p.read_text(encoding="utf-8"))
