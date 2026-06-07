from fastapi import APIRouter

from app.services.stock_service import get_tickers


router = APIRouter()


@router.get("/")
def root():
    return {"message": "Trading platform backend running"}


@router.get("/tickers")
def tickers():
    return get_tickers()
