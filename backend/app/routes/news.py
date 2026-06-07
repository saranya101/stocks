from fastapi import APIRouter

from app.services.news_service import (
    get_ai_market_news,
    get_ai_news_sentiment,
    get_news_sentiment,
)


router = APIRouter()


@router.get("/news-sentiment/{ticker}")
def news_sentiment(ticker: str):
    return get_news_sentiment(ticker)


@router.get("/ai-news-sentiment/{ticker}")
def ai_news_sentiment(ticker: str):
    return get_ai_news_sentiment(ticker)


@router.get("/ai-market-news")
def ai_market_news(
    tickers: str = "AAPL,MSFT,NVDA,GOOGL,AMZN,META,TSLA,AMD,SPY,QQQ",
):
    return get_ai_market_news(tickers)
