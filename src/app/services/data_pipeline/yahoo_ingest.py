# backend/app/services/data_pipeline/yahoo_ingest.py

from __future__ import annotations

import pandas as pd
import yfinance as yf
import pytz
from typing import Iterable, List

# 台北時區
TZ_TAIPEI = pytz.timezone("Asia/Taipei")


def as_vendor_candidates(code_or_symbol: str) -> List[str]:
    """
    將輸入轉成可能的 Yahoo Finance 代碼列表。
    - 若已含 .TW/.TWO，直接回傳 [原字串]
    - 若是純數字，例如 '2330'，回傳 ['2330.TW', '2330.TWO']（先試上市，再試上櫃）
    - 其他情況一律視為單一候選
    """
    s = code_or_symbol.strip()
    if "." in s:
        return [s]
    if s.isdigit():
        return [f"{s}.TW", f"{s}.TWO"]
    return [s]


def _flatten_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    yfinance 在某些版本會回 MultiIndex 欄位 (Price, Ticker)。
    這裡僅保留第一層 (Open/High/Low/Close/Adj Close/Volume)。
    """
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0] for c in df.columns]
    return df


def fetch_daily_ohlcv(code_or_symbol: str, start: str, end: str) -> pd.DataFrame:
    """
    從 Yahoo Finance 抓取日線行情，回傳 DataFrame
    欄位: date, open, high, low, close, adj_close, volume, source
    index: 轉為 Asia/Taipei 的日期（回傳前 reset_index）
    - code_or_symbol: 可傳 '2330' 或 '2330.TW' / '2330.TWO'
    - start, end: 'YYYY-MM-DD'
    """
    candidates = as_vendor_candidates(code_or_symbol)
    df = None

    for sym in candidates:
        try:
            data = yf.download(
                sym,
                start=start,
                end=end,
                interval="1d",
                progress=False,
                auto_adjust=False,  # 不自動復權，保留 Close 與 Adj Close
                actions=False,
                group_by="column",
            )
            if data is not None and not data.empty:
                df = data
                break
        except Exception as e:
            print(f"[yahoo_ingest] 嘗試 {sym} 失敗: {e}")
            continue

    if df is None or df.empty:
        raise ValueError(f"[yahoo_ingest] 找不到代碼 {code_or_symbol} 的行情資料")

    # 攤平欄位（避免 MultiIndex）
    df = _flatten_columns(df)

    # 正規化欄位命名
    df = df.rename(
        columns={
            "Open": "open",
            "High": "high",
            "Low": "low",
            "Close": "close",
            "Adj Close": "adj_close",
            "Volume": "volume",
        }
    )

    # 若沒有 adj_close，就用 close 當作 fallback（避免 KeyError）
    if "adj_close" not in df.columns and "close" in df.columns:
        df["adj_close"] = df["close"]

    # 轉時區：index 可能是 naive 或 UTC，統一轉成台北時區的日曆日
    idx = pd.to_datetime(df.index)
    if idx.tz is None:
        idx = idx.tz_localize("UTC")
    df.index = idx.tz_convert(TZ_TAIPEI)

    # 產出日期欄（以台北日曆日）
    df["date"] = pd.to_datetime(df.index).tz_convert(TZ_TAIPEI).tz_localize(None).normalize()

    # 標記資料來源
    df["source"] = "yahoo"

    # 確保欄位齊全
    for col in ["open", "high", "low", "close", "adj_close", "volume"]:
        if col not in df.columns:
            df[col] = pd.NA

    # 只保留必要欄位並回傳
    df = df[["date", "open", "high", "low", "close", "adj_close", "volume", "source"]]
    return df.reset_index(drop=True)


__all__ = ["fetch_daily_ohlcv", "as_vendor_candidates"]