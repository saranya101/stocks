from fastapi import APIRouter

from app.database import SessionLocal
from app.models.market_scan import MarketScan
from app.models.watchlist import WatchlistItem
from app.services.dashboard_service import get_trade_opportunities

router = APIRouter()


@router.get("/dashboard")
def get_dashboard():
    db = SessionLocal()

    try:
        latest_scan = (
            db.query(MarketScan)
            .order_by(MarketScan.created_at.desc())
            .first()
        )

        watchlist_items = db.query(WatchlistItem).all()
        watchlist = [item.ticker.upper() for item in watchlist_items]

        scan_results = latest_scan.results if latest_scan else []

        market_opportunities = [
            item for item in scan_results
            if item.get("ticker") not in watchlist
        ]

        trade_opportunities = get_trade_opportunities(
            tickers=watchlist if watchlist else None
        )

        top_pick = trade_opportunities[0] if trade_opportunities else None

        buy_count = len([
            item for item in trade_opportunities
            if item.get("signal") == "BUY"
        ])

        watch_count = len([
            item for item in trade_opportunities
            if item.get("signal") == "WATCH"
        ])

        avoid_count = len([
            item for item in trade_opportunities
            if item.get("signal") == "AVOID"
        ])

        return {
            "brief": {
                "top_pick": top_pick,
                "buy_count": buy_count,
                "watch_count": watch_count,
                "avoid_count": avoid_count,
                "last_scan_at": latest_scan.created_at if latest_scan else None,
            },
            "watchlist": watchlist,
            "trade_opportunities": trade_opportunities,
            "market_opportunities": market_opportunities[:20],
            "alerts": [],
        }

    finally:
        db.close()