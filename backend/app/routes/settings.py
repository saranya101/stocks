from fastapi import APIRouter
from pydantic import BaseModel
from app.database import SessionLocal
from app.models.settings import AppSettings

router = APIRouter()


class SettingsUpdate(BaseModel):
    universe: str = "us_largecap"
    scan_mode: str = "fast"
    scan_limit: int = 50
    fast: int = 5
    slow: int = 30
    rsi_sell: int = 70
    stop_loss: float = 0.03


def serialize_settings(settings: AppSettings):
    return {
        "universe": settings.universe,
        "scanMode": settings.scan_mode,
        "scanLimit": settings.scan_limit,
        "fast": settings.fast,
        "slow": settings.slow,
        "rsiSell": settings.rsi_sell,
        "stopLoss": settings.stop_loss,
        "updatedAt": settings.updated_at,
    }


@router.get("/settings")
def get_settings():
    db = SessionLocal()

    try:
        settings = db.query(AppSettings).first()

        if not settings:
            settings = AppSettings()
            db.add(settings)
            db.commit()
            db.refresh(settings)

        return serialize_settings(settings)

    finally:
        db.close()


@router.put("/settings")
def update_settings(payload: SettingsUpdate):
    db = SessionLocal()

    try:
        settings = db.query(AppSettings).first()

        if not settings:
            settings = AppSettings()
            db.add(settings)

        settings.universe = payload.universe
        settings.scan_mode = payload.scan_mode
        settings.scan_limit = payload.scan_limit
        settings.fast = payload.fast
        settings.slow = payload.slow
        settings.rsi_sell = payload.rsi_sell
        settings.stop_loss = payload.stop_loss

        db.commit()
        db.refresh(settings)

        return serialize_settings(settings)

    finally:
        db.close()