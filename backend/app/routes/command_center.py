from fastapi import APIRouter
from app.services.command_center_service import get_command_center

router = APIRouter()


@router.get("/command-center")
def command_center(
    market: str = "us",
    limit: int = 50,
    timeframe: str = "5m",
):
    return get_command_center(
        market=market,
        limit=limit,
        timeframe=timeframe,
    )