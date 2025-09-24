# backend/app/services/resolve.py
from __future__ import annotations
import re
from typing import Dict, List, Optional, Tuple

# 四碼代號
CODE_RE = re.compile(r"^\d{4}$")

# 支援舊尾碼
def _strip_suffix(s: str) -> Optional[str]:
    s = s.strip().upper()
    for suf in (".TW", ".TWO"):
        if s.endswith(suf):
            core = s[: -len(suf)]
            return core if CODE_RE.match(core) else None
    return None

# 最小別名表（Phase0：只放測試會用到的幾個）
NAME_TO_CODE: Dict[str, str] = {
    "台積": "2330",
    "台積電": "2330",
    "國泰金": "2882",
    "鴻海": "2317",
    "聯發科": "2454",
    "富邦金": "2881",
    "中鋼": "2002",
    "長榮": "2603",
    "陽明": "2609",
}

def normalize_code_or_name(q: str) -> Tuple[Optional[str], List[Dict[str, str]]]:
    """
    將輸入（四碼/中文/2330.TW）解析為標準 code。
    回傳:
      - 唯一命中: ("2330", [])
      - 多筆歧義: (None, [{"code":"2330","name":"台積電"}, ...])  # 目前不做歧義，回 []
      - 無命中:    (None, [])
    Phase0：純函式，不連 DB。
    """
    if not q:
        return None, []
    s = q.strip()

    # 1) 剝舊尾碼
    suf = _strip_suffix(s)
    if suf:
        s = suf

    # 2) 四位數直接回傳
    if CODE_RE.match(s):
        return s, []

    # 3) 中文名稱/別名 → 查最小別名表（大小寫與空白已處理）
    code = NAME_TO_CODE.get(s)
    if code:
        return code, []

    # 4) 其他：無命中
    return None, []