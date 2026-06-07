from fastapi import APIRouter
from app.database import SessionLocal
from app.models.watchlist import WatchlistItem

router = APIRouter()


@router.get("/watchlist")
def get_watchlist():
    db = SessionLocal()

    try:
        items = (
            db.query(WatchlistItem)
            .order_by(WatchlistItem.created_at.asc())
            .all()
        )

        return {
            "watchlist": [
                item.ticker
                for item in items
            ]
        }

    finally:
        db.close()


@router.post("/watchlist/add")
def add_to_watchlist(ticker: str):
    db = SessionLocal()

    try:
        ticker = ticker.upper().strip()

        existing = (
            db.query(WatchlistItem)
            .filter(WatchlistItem.ticker == ticker)
            .first()
        )

        if existing:
            return {
                "message": "Ticker already exists",
                "ticker": ticker
            }

        item = WatchlistItem(ticker=ticker)

        db.add(item)
        db.commit()

        return {
            "message": "Ticker added",
            "ticker": ticker
        }

    finally:
        db.close()


@router.delete("/watchlist/remove/{ticker}")
def remove_from_watchlist(ticker: str):
    db = SessionLocal()

    try:
        ticker = ticker.upper().strip()

        item = (
            db.query(WatchlistItem)
            .filter(WatchlistItem.ticker == ticker)
            .first()
        )

        if not item:
            return {
                "message": "Ticker not found",
                "ticker": ticker
            }

        db.delete(item)
        db.commit()

        return {
            "message": "Ticker removed",
            "ticker": ticker
        }

    finally:
        db.close()