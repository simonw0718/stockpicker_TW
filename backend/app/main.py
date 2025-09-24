# backend/app/main.py 
from fastapi import FastAPI

import backend.app.routers.symbols as symbols
import backend.app.routers.watchlist as watchlist
import backend.app.routers.strategies as strategies
import backend.app.routers.alerts as alerts

app = FastAPI(title="StockPicker TW API", version="0.1.0")

@app.get("/api/v1/health")
def health():
    return {"status": "ok"}

# symbols：/api/v1/symbols/search
app.include_router(symbols.router,    prefix="/api/v1/symbols",    tags=["symbols"])
# watchlist（schema_v2）：/api/v1/watchlist/...
app.include_router(watchlist.router,  prefix="/api/v1/watchlist",  tags=["watchlist"])
# 其他
app.include_router(strategies.router, prefix="/api/v1/strategies", tags=["strategies"])
app.include_router(alerts.router,     prefix="/api/v1/alerts",     tags=["alerts"])