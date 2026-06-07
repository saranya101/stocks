from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine
from app.routes import chart
from app.models import Base
from app.routes import universe
from app.routes import settings
from app.routes.universe import router as universe_router
from app.services.scheduler_service import start_scanner_scheduler
from app.routes import scanner_settings
from app.routes import scanner
from app.routes import trade_plans

from app.routes import dashboard
from app.routes import (
    backtests,
    command_center,
    news,
    opportunities,
    stocks,
    system,
    watchlist,
)


Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.on_event("startup")
def start_background_jobs():
    start_scanner_scheduler()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(system.router)
app.include_router(chart.router)
app.include_router(stocks.router)
app.include_router(backtests.router)
app.include_router(opportunities.router)
app.include_router(news.router)
app.include_router(scanner.router)
app.include_router(command_center.router)
app.include_router(watchlist.router)
app.include_router(universe.router)
app.include_router(universe_router)
app.include_router(settings.router)
app.include_router(dashboard.router)
app.include_router(scanner_settings.router)
app.include_router(trade_plans.router)