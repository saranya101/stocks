from fastapi import APIRouter
from pydantic import BaseModel

from app.database import SessionLocal
from app.models.scanner_settings import ScannerSettings

router = APIRouter(prefix="/scanner-settings", tags=["scanner-settings"])


class ScannerSettingsUpdate(BaseModel):
    enabled: bool
    scan_interval_minutes: int
    scan_us: bool
    scan_sg: bool
    scan_etf: bool
    scan_crypto: bool
    max_tickers_per_market: int
    max_results_per_market: int


def get_or_create_settings(db):
    settings = db.query(ScannerSettings).first()

    if not settings:
        settings = ScannerSettings()
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings


@router.get("")
def get_scanner_settings():
    db = SessionLocal()

    try:
        settings = get_or_create_settings(db)

        return {
            "enabled": settings.enabled,
            "scan_interval_minutes": settings.scan_interval_minutes,
            "scan_us": settings.scan_us,
            "scan_sg": settings.scan_sg,
            "scan_etf": settings.scan_etf,
            "scan_crypto": settings.scan_crypto,
            "max_tickers_per_market": settings.max_tickers_per_market,
            "max_results_per_market": settings.max_results_per_market,
            "updated_at": settings.updated_at,
        }

    finally:
        db.close()


@router.put("")
def update_scanner_settings(payload: ScannerSettingsUpdate):
    db = SessionLocal()

    try:
        settings = get_or_create_settings(db)

        settings.enabled = payload.enabled
        settings.scan_interval_minutes = payload.scan_interval_minutes
        settings.scan_us = payload.scan_us
        settings.scan_sg = payload.scan_sg
        settings.scan_etf = payload.scan_etf
        settings.scan_crypto = payload.scan_crypto
        settings.max_tickers_per_market = payload.max_tickers_per_market
        settings.max_results_per_market = payload.max_results_per_market

        db.commit()
        db.refresh(settings)

        return {
            "message": "Scanner settings updated",
            "settings": {
                "enabled": settings.enabled,
                "scan_interval_minutes": settings.scan_interval_minutes,
                "scan_us": settings.scan_us,
                "scan_sg": settings.scan_sg,
                "scan_etf": settings.scan_etf,
                "scan_crypto": settings.scan_crypto,
                "max_tickers_per_market": settings.max_tickers_per_market,
                "max_results_per_market": settings.max_results_per_market,
                "updated_at": settings.updated_at,
            },
        }

    finally:
        db.close()