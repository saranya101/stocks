from fastapi import APIRouter

from app.services.persistent_scanner_service import (
    run_persistent_scan,
    get_latest_persistent_scan,
)

router = APIRouter()


@router.post("/scanner/run")
def scanner_run(
    market: str = "us",
    limit: int = 200,
    timeframe: str = "5m",
):
    return run_persistent_scan(
        market=market,
        limit=limit,
        timeframe=timeframe,
    )


@router.get("/scanner/latest")
def scanner_latest(
    market: str = "us",
):
    return get_latest_persistent_scan(
        market=market,
    )