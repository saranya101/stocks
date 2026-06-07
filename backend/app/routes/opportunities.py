from fastapi import APIRouter

from app.database import SessionLocal
from app.models.market_scan import MarketScan
from app.services.opportunity_service import get_ai_opportunities
from app.services.opportunity_service import SCAN_STATUS

router = APIRouter()


@router.get("/ai-opportunities")
def ai_opportunities(
    limit: int = 50,
    tickers: str = "",
    fast: int = 5,
    slow: int = 30,
    rsi_sell: int = 70,
    stop_loss: float = 0.03,
    trend_weight: float = 15,
    momentum_weight: float = 10,
    backtest_weight: float = 15,
    risk_penalty: float = 15,
    win_rate_weight: float = 10,
    rsi_danger_level: float = 80,
    scan_mode: str = "deep",
    max_drawdown_allowed: float = 20,
):
    return get_ai_opportunities(
        limit=limit,
        tickers=tickers,
        fast=fast,
        slow=slow,
        rsi_sell=rsi_sell,
        stop_loss=stop_loss,
        trend_weight=trend_weight,
        momentum_weight=momentum_weight,
        backtest_weight=backtest_weight,
        risk_penalty=risk_penalty,
        win_rate_weight=win_rate_weight,
        rsi_danger_level=rsi_danger_level,
        scan_mode=scan_mode,
        max_drawdown_allowed=max_drawdown_allowed,
    )


@router.get("/ai-opportunities/latest")
def latest_ai_opportunities():
    from app.database import SessionLocal
    from app.models import AIScanResult
    from app.models.watchlist import WatchlistItem

    db = SessionLocal()

    try:
        watchlist_items = db.query(WatchlistItem).all()
        watchlist = [item.ticker for item in watchlist_items]

        if not watchlist:
            return {
                "market_scan_size": 0,
                "top_opportunities": []
            }

        rows = (
            db.query(AIScanResult)
            .filter(AIScanResult.ticker.in_(watchlist))
            .order_by(AIScanResult.created_at.desc())
            .all()
        )

        latest_by_ticker = {}

        for item in rows:
            if item.ticker not in latest_by_ticker:
                latest_by_ticker[item.ticker] = item

        results = list(latest_by_ticker.values())

        results = sorted(
            results,
            key=lambda x: x.confidence,
            reverse=True
        )

        return {
            "market_scan_size": len(results),
            "top_opportunities": [
                {
                    "ticker": item.ticker,
                    "confidence": item.confidence,
                    "signal": item.signal,
                    "risk_level": item.risk_level,
                    "price": item.price,
                    "rsi": item.rsi,
                    "backtest_return": item.backtest_return,
                    "max_drawdown": item.max_drawdown,
                    "win_rate": item.win_rate,
                    "created_at": item.created_at,
                    "reasons": [],
                    "news_score": 0,
                    "news_label": "SAVED SCAN",
                    "news_confidence": 0,
                    "news_articles": []
                }
                for item in results
            ]
        }

    finally:
        db.close()

@router.get("/latest-market-scan")
def latest_market_scan():
    db = SessionLocal()

    try:
        latest = (
            db.query(MarketScan)
            .order_by(MarketScan.created_at.desc())
            .first()
        )

        if not latest:
            return {
                "created_at": None,
                "universe": None,
                "scan_mode": None,
                "opportunities": [],
            }

        return {
            "created_at": latest.created_at,
            "universe": latest.universe,
            "scan_mode": latest.scan_mode,
            "opportunities": latest.results or [],
        }

    finally:
        db.close()

        
@router.get("/scan-status")
def scan_status():
    return SCAN_STATUS