# src/app/main.py
from fastapi import FastAPI
from app.routers import symbols, watchlist, strategies, alerts, backtest, scan, signals
from app.routers import metrics  # ← 新增

app = FastAPI(title="StockPicker TW API", version="0.1.0")

@app.get("/api/v1/health")
def health():
    return {"status": "ok"}

# Mount routers
app.include_router(symbols.router)
app.include_router(watchlist.router)
app.include_router(strategies.router)
app.include_router(alerts.router)
app.include_router(backtest.router)
app.include_router(scan.router)
app.include_router(signals.router)
app.include_router(metrics.router)  # ← 新增