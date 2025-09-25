from fastapi import FastAPI
from app.routers import symbols, watchlist, strategies, alerts

app = FastAPI(title="StockPicker TW API", version="0.1.0")

@app.get("/api/v1/health")
def health():
    return {"status": "ok"}

# Mount routers
app.include_router(symbols.router,    prefix="/api/v1/symbols",    tags=["symbols"])
app.include_router(watchlist.router,  prefix="/api/v1/watchlist",  tags=["watchlist"])
app.include_router(strategies.router, prefix="/api/v1/strategies", tags=["strategies"])
app.include_router(alerts.router,     prefix="/api/v1/alerts",     tags=["alerts"])
