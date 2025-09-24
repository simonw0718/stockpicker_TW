# backend/app/services/data_pipeline/duckdb_io.py
from pathlib import Path
import duckdb
import pandas as pd


# 回到專案根需要往上 4 層
ROOT = Path(__file__).resolve().parents[4]
PARQUET_DIR = ROOT / "data" / "parquet"

def read_ohlcv(code: str, start: str | None = None, end: str | None = None, limit: int | None = None) -> pd.DataFrame:
    """
    從 data/parquet/{code}.parquet 讀取 OHLCV
    可選 start/end（YYYY-MM-DD）與 limit。
    """
    path = PARQUET_DIR / f"{code}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Parquet not found for code={code}: {path}")

    con = duckdb.connect(database=":memory:")
    query = f"SELECT * FROM read_parquet('{path.as_posix()}')"

    where = []
    if start:
        where.append(f"date >= '{start}'")
    if end:
        where.append(f"date <= '{end}'")
    if where:
        query += " WHERE " + " AND ".join(where)

    query += " ORDER BY date"
    if limit:
        query += f" LIMIT {int(limit)}"

    df = con.execute(query).df()
    return df