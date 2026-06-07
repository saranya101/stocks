import time
import uuid
from datetime import datetime, timezone

from app.database import SessionLocal
from app.models.market_opportunity import MarketOpportunity
from app.models.scan_status import ScanStatus
from app.services.market_universe_service import get_market_universe
from app.services.two_stage_scanner_service import run_two_stage_scan


def run_persistent_scan(
    market: str = "us",
    limit: int = 200,
    timeframe: str = "5m",
):
    db = SessionLocal()

    scan_id = str(uuid.uuid4())
    started_at = datetime.now(timezone.utc)
    start_time = time.time()

    status = ScanStatus(
        scan_id=scan_id,
        market=market,
        status="RUNNING",
        started_at=started_at,
    )

    db.add(status)
    db.commit()

    try:
        tickers = get_market_universe(
    market=market,
    limit=limit,
)

        result = run_two_stage_scan(
            tickers=tickers[:limit],
            timeframe=timeframe,
            deep_limit=50,
            final_limit=20,
        )

        raw_opportunities = result.get("opportunities", [])

        opportunities = [
            item for item in raw_opportunities
            if item.get("recommendation") in ["STRONG BUY", "BUY", "WATCH"]
            and item.get("shares", 0) > 0
            and item.get("conviction", 0) >= 60
            and item.get("direction") == "LONG"
        ]

        opportunities = sorted(
            opportunities,
            key=lambda item: item.get("conviction", 0),
            reverse=True,
        )[:20]

        for item in opportunities:
            db.add(
                MarketOpportunity(
                    scan_id=scan_id,
                    market=market,
                    ticker=item.get("ticker"),
                    direction=item.get("direction"),
                    conviction=item.get("conviction"),
                    probability=item.get("probability"),
                    grade=item.get("grade"),
                    recommendation=item.get("recommendation"),
                    entry_price=item.get("entry_price"),
                    stop_loss=item.get("stop_loss"),
                    take_profit=item.get("take_profit"),
                    risk_reward=item.get("risk_reward"),
                    expected_hold_days=item.get("expected_hold_days"),
                    status=item.get("status"),
                    technical_score=item.get("technical_score"),
                    backtest_score=item.get("backtest_score"),
                    news_score=item.get("news_score"),
                    volume_score=item.get("volume_score"),
                    reasons=item.get("reasons", []),
                    raw_data=item,
                )
            )

        status.status = "COMPLETED"
        status.total_scanned = result.get("fast_scanned", len(tickers))
        status.opportunities_found = len(opportunities)
        status.duration_seconds = round(time.time() - start_time, 2)
        status.completed_at = datetime.now(timezone.utc)

        db.commit()

        return {
            "scan_id": scan_id,
            "status": "COMPLETED",
            "market": market,
            "saved": len(opportunities),
        }

    except Exception as error:
        status.status = "FAILED"
        status.duration_seconds = round(time.time() - start_time, 2)
        status.completed_at = datetime.now(timezone.utc)

        db.commit()

        return {
            "scan_id": scan_id,
            "status": "FAILED",
            "error": str(error),
        }

    finally:
        db.close()


def get_latest_persistent_scan(market: str = "us"):
    db = SessionLocal()

    try:
        latest_status = (
            db.query(ScanStatus)
            .filter(ScanStatus.market == market)
            .order_by(ScanStatus.started_at.desc())
            .first()
        )

        if not latest_status:
            return {
                "scan_status": None,
                "opportunities": [],
            }

        opportunities = (
            db.query(MarketOpportunity)
            .filter(MarketOpportunity.scan_id == latest_status.scan_id)
            .order_by(MarketOpportunity.conviction.desc())
            .all()
        )

        return {
            "scan_status": {
                "scan_id": latest_status.scan_id,
                "market": latest_status.market,
                "status": latest_status.status,
                "total_scanned": latest_status.total_scanned,
                "opportunities_found": latest_status.opportunities_found,
                "duration_seconds": latest_status.duration_seconds,
                "started_at": latest_status.started_at,
                "completed_at": latest_status.completed_at,
            },
            "opportunities": [item.raw_data for item in opportunities],
        }

    finally:
        db.close()