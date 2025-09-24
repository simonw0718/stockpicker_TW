from .registry import register
from . import registry

from .builtin.ma import compute as _ma
from .builtin.ema import compute as _ema
from .builtin.rsi import compute as _rsi
from .builtin.macd import compute as _macd
from .builtin.boll import compute as _boll
from .builtin.bias import compute as _bias
from .builtin.volume import compute as _volume
from .builtin.diff import compute as _diff

# 單欄
register("MA",   _ma,   {"timeframes":["1d"], "fields": None, "default_field": None, "warmup": lambda p: int(p["window"])-1})
register("EMA",  _ema,  {"timeframes":["1d"], "fields": None, "default_field": None, "warmup": lambda p: int(p["window"])-1})
register("RSI",  _rsi,  {"timeframes":["1d"], "fields": None, "default_field": None, "warmup": lambda p: int(p["period"])})
register("BIAS", _bias, {"timeframes":["1d"], "fields": None, "default_field": None, "warmup": lambda p: int(p["window"])-1})
register("VOLUME", _volume, {"timeframes":["1d"], "fields": None, "default_field": None, "warmup": lambda p: (int(p["window"])-1) if p.get("window") else 0})
register("DIFF", _diff, {"timeframes":["1d"], "fields": None, "default_field": None, "warmup": lambda p: 0})

# 多欄
register("MACD", _macd, {"timeframes":["1d"], "fields": ["macd","signal","hist"], "default_field":"macd", "warmup": lambda p: max(int(p["slow"])-1, int(p["signal"])-1)})
register("BOLL", _boll, {"timeframes":["1d"], "fields": ["upper","middle","lower"], "default_field":"middle", "warmup": lambda p: int(p["window"])-1})
