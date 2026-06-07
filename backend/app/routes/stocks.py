from fastapi import APIRouter

from app.services.stock_service import (
    get_analysis,
    get_scanner_results,
    get_stock_data,
    get_stock_detail,
)


router = APIRouter()


@router.get("/stocks/{ticker}")
def stock_data(ticker: str):
    return get_stock_data(ticker)


@router.get("/analysis/{ticker}")
def analysis(ticker: str):
    return get_analysis(ticker)


@router.get("/scanner")
def scanner(limit: int = 25):
    return get_scanner_results(limit=limit)


@router.get("/stock-detail/{ticker}")
def stock_detail(ticker: str):
    return get_stock_detail(ticker)
