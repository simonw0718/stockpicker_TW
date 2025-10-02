# src/app/config.py
import os

def get_env_int(key: str, default: int) -> int:
    """
    從環境變數讀取整數；無值或格式錯誤時回傳 default。
    """
    val = os.getenv(key, "")
    try:
        return int(val)
    except Exception:
        return int(default)