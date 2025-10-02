# src/app/indicators/__init__.py
"""
Indicators package bootstrap:
- 暴露 registry 物件
- 匯入並註冊內建指標（名稱大小寫不敏感；一律以小寫註冊）
"""

from . import registry  # re-export

# ---- import builtin modules ----
from .builtin import ma as _ma
from .builtin import ema as _ema
from .builtin import rsi as _rsi
from .builtin import macd as _macd
from .builtin import boll as _boll
from .builtin import bias as _bias
from .builtin import volume as _volume
from .builtin import diff as _diff

# ---- register all builtins (keys in lowercase) ----
registry.register(
    name="ma",
    fn=_ma.compute,
    meta={
        "timeframes": ["1d"],
        "fields": None,
        "default_field": None,
        "warmup": lambda p: int((p or {}).get("window", 5)),
    },
)

registry.register(
    name="ema",
    fn=_ema.compute,
    meta={
        "timeframes": ["1d"],
        "fields": None,
        "default_field": None,
        "warmup": lambda p: int((p or {}).get("window", 5)),
    },
)

registry.register(
    name="rsi",
    fn=_rsi.compute,
    meta={
        "timeframes": ["1d"],
        "fields": None,
        "default_field": None,
        "warmup": lambda p: int((p or {}).get("period", 14)),
    },
)

registry.register(
    name="macd",
    fn=_macd.compute,
    meta={
        "timeframes": ["1d"],
        "fields": ["macd", "signal", "hist"],
        "default_field": "macd",
        "warmup": lambda p: max(int((p or {}).get("fast", 12)), int((p or {}).get("slow", 26))) + int((p or {}).get("signal", 9)),
    },
)

registry.register(
    name="boll",
    fn=_boll.compute,
    meta={
        "timeframes": ["1d"],
        "fields": ["middle", "upper", "lower"],
        "default_field": "middle",
        "warmup": lambda p: int((p or {}).get("window", 20)),
    },
)

registry.register(
    name="bias",
    fn=_bias.compute,
    meta={
        "timeframes": ["1d"],
        "fields": None,
        "default_field": None,
        "warmup": lambda p: int((p or {}).get("window", 20)),
    },
)

registry.register(
    name="volume",
    fn=_volume.compute,
    meta={
        "timeframes": ["1d"],
        # 內建 volume 常見回傳 raw / ma
        "fields": ["raw", "ma"],
        "default_field": "raw",
        "warmup": lambda p: int((p or {}).get("window", 5)),
    },
)

registry.register(
    name="diff",
    fn=_diff.compute,
    meta={
        "timeframes": ["1d"],
        "fields": None,
        "default_field": None,
        "warmup": lambda p: 1,
    },
)