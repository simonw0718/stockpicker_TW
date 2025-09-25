# src/app/domain/strategies/validation.py
from typing import List, Literal, Optional, Union, Dict, Any, Callable
from pydantic import BaseModel, validator, root_validator, ValidationError

# ============================================================
# 可覆蓋/可擴充：指標規格與註冊表
# ============================================================

class IndicatorSpec(BaseModel):
    """單一指標的驗證規格與欄位行為"""
    # 用 validator_fn 避開 BaseModel.validate 衝突
    validator_fn: Callable[[Dict[str, Any]], None]
    # 多欄輸出時可用欄位（None 代表單欄輸出）
    fields: Optional[List[str]] = None
    # 如未指定 field 時的預設欄位（僅 fields 非空時生效）
    default_field: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True


# 內建規則（可在專案啟動時被覆蓋/延伸）
INDICATOR_SPECS: Dict[str, IndicatorSpec] = {}

def register_indicator(name: str, spec: IndicatorSpec, overwrite: bool = True) -> None:
    """註冊或覆寫指標規格；overwrite=False 時保護既有條目"""
    if not overwrite and name in INDICATOR_SPECS:
        return
    INDICATOR_SPECS[name] = spec


# ---- 內建參數檢查工具 ----
def _req_int(params: Dict[str, Any], name: str, lo: int, hi: int) -> int:
    val = params.get(name)
    if not isinstance(val, int):
        raise ValueError(f'{name} must be integer')
    if not (lo <= val <= hi):
        raise ValueError(f'{name} out of range [{lo},{hi}]')
    return val

def _req_num(params: Dict[str, Any], name: str, lo: float, hi: float) -> float:
    val = params.get(name)
    if not isinstance(val, (int, float)):
        raise ValueError(f'{name} must be number')
    v = float(val)
    if not (lo <= v <= hi):
        raise ValueError(f'{name} out of range [{lo},{hi}]')
    return v

# ---- 內建指標規格（預設）----
def _spec_MA(params: Dict[str, Any]) -> None:
    _req_int(params, 'window', 2, 400)

def _spec_EMA(params: Dict[str, Any]) -> None:
    _req_int(params, 'window', 2, 400)

def _spec_RSI(params: Dict[str, Any]) -> None:
    _req_int(params, 'period', 2, 250)

def _spec_MACD(params: Dict[str, Any]) -> None:
    fast = _req_int(params, 'fast',   2, 400)
    slow = _req_int(params, 'slow',   2, 400)
    _req_int(params, 'signal', 2, 200)
    if not (fast < slow):
        # 1A/Level2：直接視為參數關係錯誤
        raise ValueError('fast must be less than slow')

def _spec_BOLL(params: Dict[str, Any]) -> None:
    _req_int(params, 'window', 5, 400)
    _req_num(params, 'mult', 0.5, 5.0)

def _spec_KD(params: Dict[str, Any]) -> None:
    _req_int(params, 'k_period', 2, 200)
    _req_int(params, 'd_period', 2, 200)
    smooth = params.get('smooth', 1)
    if not isinstance(smooth, int):
        raise ValueError('smooth must be integer')
    if not (1 <= smooth <= 20):
        raise ValueError('smooth out of range [1,20]')

def _spec_BIAS(params: Dict[str, Any]) -> None:
    _req_int(params, 'window', 2, 400)

def _spec_VOLUME(params: Dict[str, Any]) -> None:
    w = params.get('window', None)
    if w is not None:
        if not isinstance(w, int):
            raise ValueError('window must be integer')
        if not (2 <= w <= 400):
            raise ValueError('window out of range [2,400]')

def _spec_DIFF(params: Dict[str, Any]) -> None:
    # 1A 僅檢查必要鍵存在；細節相容性延到 1C
    if params.get('left') is None or params.get('right') is None:
        raise ValueError("DIFF.params must include 'left' and 'right'")

# 註冊內建
register_indicator('MA',     IndicatorSpec(validator_fn=_spec_MA))
register_indicator('EMA',    IndicatorSpec(validator_fn=_spec_EMA))
register_indicator('RSI',    IndicatorSpec(validator_fn=_spec_RSI))
register_indicator('MACD',   IndicatorSpec(validator_fn=_spec_MACD, fields=['macd','signal','hist'], default_field='macd'))
register_indicator('BOLL',   IndicatorSpec(validator_fn=_spec_BOLL, fields=['upper','middle','lower'], default_field='middle'))
register_indicator('KD',     IndicatorSpec(validator_fn=_spec_KD,   fields=['k','d'], default_field='k'))
register_indicator('BIAS',   IndicatorSpec(validator_fn=_spec_BIAS))
register_indicator('VOLUME', IndicatorSpec(validator_fn=_spec_VOLUME))
register_indicator('DIFF',   IndicatorSpec(validator_fn=_spec_DIFF))


# ============================================================
# Pydantic 模型（保持 1A 合約）
# ============================================================

class NumberOperand(BaseModel):
    value: float
    @validator('value')
    def _range(cls, v):
        if v < -1e9 or v > 1e9:
            raise ValueError('value out of range [-1e9, 1e9]')
        return v

class SeriesRefOperand(BaseModel):
    series: Literal['open','high','low','close','volume']

class IndicatorRefOperand(BaseModel):
    indicator: Literal['MA','EMA','RSI','MACD','BOLL','KD','BIAS','VOLUME','DIFF']
    params: Dict[str, Any]
    source: Optional[Literal['close','open','high','low','typical','hlc3']] = 'close'
    field: Optional[str] = None

    @validator('params')
    def _validate_params_with_spec(cls, v, values):
        ind = values.get('indicator')
        spec = INDICATOR_SPECS.get(ind)
        if spec is None:
            # 依 1A 範圍，這裡理論上不會發生
            raise ValueError(f'unknown indicator: {ind}')
        spec.validator_fn(v)  # 不合法 raise
        return v

    @root_validator(skip_on_failure=True)
    def _apply_field_policy(cls, values):
        ind   = values.get('indicator')
        field = values.get('field')
        spec  = INDICATOR_SPECS.get(ind)
        if spec and spec.fields:
            # 多欄輸出：套用預設或檢查合法性
            if field is None:
                values['field'] = spec.default_field or spec.fields[0]
            elif field not in spec.fields:
                raise ValueError(f"field must be one of {spec.fields} for {ind}")
        else:
            # 單欄輸出：不應該指定 field
            if field is not None:
                raise ValueError(f"{ind} does not support 'field'")
        return values

Operand = Union[NumberOperand, SeriesRefOperand, IndicatorRefOperand]

class Condition(BaseModel):
    left: Operand
    op: Literal['>','<','>=','<=','==','!=','cross_up','cross_down']
    right: Operand
    note: Optional[str] = None

    @root_validator(skip_on_failure=True)
    def _check_op_compatibility(cls, values):
        op = values.get('op')
        left = values.get('left')
        right = values.get('right')
        # 1A：交叉不接受數值
        if op in ('cross_up','cross_down'):
            if isinstance(left, NumberOperand) or isinstance(right, NumberOperand):
                raise ValueError("cross_* operator requires two series operands")
        return values

class Strategy(BaseModel):
    name: str
    version: str
    type: Literal['screen','backtest']
    timeframe: Literal['1d']  # 1A 固定
    logic: Literal['AND','OR']
    conditions: List[Condition]
    description: Optional[str] = None
    universe: Optional[dict] = None
    params: Optional[dict] = None
    metadata: Optional[dict] = None

    @validator('name')
    def _name_rules(cls, v):
        if not (3 <= len(v) <= 64):
            raise ValueError('name length must be between 3 and 64')
        return v

    @validator('version')
    def _version_format(cls, v):
        parts = v.split('.')
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            raise ValueError("version must be 'major.minor.patch' numeric")
        return v

    @validator('conditions')
    def _min_conditions(cls, v):
        if not v or len(v) < 1:
            raise ValueError('at least one condition is required')
        return v


# ============================================================
# 錯誤轉換：對齊 docs/api/errors.md
# ============================================================

def format_validation_error(exc: ValidationError) -> dict:
    def loc_to_path(loc):
        out = []
        for part in loc:
            if isinstance(part, int):
                out[-1] = f"{out[-1]}[{part}]"
            else:
                out.append(str(part))
        return ".".join(out)

    def map_code(pyd_code: str, path: str, msg: str) -> str:
        if pyd_code.endswith(".const"):
            return "invalid_enum"
        if "out of range" in msg:
            return "out_of_range"
        if "less than slow" in msg or "must be less than slow" in msg:
            return "invalid_relation"
        if "at least one condition" in msg:
            return "missing_required"
        if "does not support 'field'" in msg:
            return "invalid_field"
        if "unknown indicator" in msg:
            return "invalid_value"
        if "requires two series operands" in msg:
            return "invalid_operand"
        if msg == "field required":
            return "missing_required"
        return "invalid_value"

    raw = []
    for e in exc.errors():
        path = loc_to_path(e['loc'])
        raw_code = e.get('type', 'value_error')
        msg = e['msg']
        code = map_code(raw_code, path, msg)
        raw.append({"path": path, "code": code, "message": msg})

    # ---- 去除 Union 嘗試造成的噪音 ----
    def lr_prefix(p: str):
        if ".left" in p:
            return p.split(".left")[0] + ".left"
        if ".right" in p:
            return p.split(".right")[0] + ".right"
        return p

    substantive = set()
    for e in raw:
        if ".params" in e["path"] or ".field" in e["path"]:
            substantive.add(lr_prefix(e["path"]))

    filtered = []
    for e in raw:
        base = lr_prefix(e["path"])
        if base in substantive and e["code"] == "missing_required" and (
            e["path"].endswith(".value") or e["path"].endswith(".series")
        ):
            continue
        filtered.append(e)

    # 去重
    unique = []
    seen = set()
    for e in filtered:
        key = (e["path"], e["code"], e["message"])
        if key not in seen:
            seen.add(key)
            unique.append(e)

    return {"status": 422, "errors": unique}