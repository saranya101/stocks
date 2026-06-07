# app/services/scheduler_service.py

import time
import threading

from app.database import SessionLocal
from app.models.scanner_settings import ScannerSettings
from app.services.persistent_scanner_service import run_persistent_scan


def get_scanner_settings():
    db = SessionLocal()

    try:
        settings = db.query(ScannerSettings).first()

        if not settings:
            settings = ScannerSettings()
            db.add(settings)
            db.commit()
            db.refresh(settings)

        return {
            "enabled": settings.enabled,
            "scan_interval_minutes": settings.scan_interval_minutes,
            "scan_us": settings.scan_us,
            "scan_sg": settings.scan_sg,
            "scan_etf": settings.scan_etf,
            "scan_crypto": settings.scan_crypto,
            "max_tickers_per_market": settings.max_tickers_per_market,
            "max_results_per_market": settings.max_results_per_market,
        }

    finally:
        db.close()


def scanner_loop():
    while True:
        settings = get_scanner_settings()

        if settings["enabled"]:
            markets = []

            if settings["scan_us"]:
                markets.append("us")

            if settings["scan_sg"]:
                markets.append("sg")

            if settings["scan_etf"]:
                markets.append("etf")

            if settings["scan_crypto"]:
                markets.append("crypto")

            for market in markets:
                print(f"AUTO SCAN STARTED: {market}")

                run_persistent_scan(
                    market=market,
                    limit=settings["max_tickers_per_market"],
                    timeframe="5m",
                )

                print(f"AUTO SCAN COMPLETED: {market}")

        sleep_seconds = max(
            1,
            settings["scan_interval_minutes"],
        ) * 60

        time.sleep(sleep_seconds)


def start_scanner_scheduler():
    thread = threading.Thread(
        target=scanner_loop,
        daemon=True,
    )

    thread.start()