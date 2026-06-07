from app.news.ai_news_analyzer import analyze_news_with_ai
from app.news.news_fetcher import fetch_stock_news
from app.news.news_sentiment import analyze_news_sentiment


def get_news_sentiment(ticker: str):
    ticker = ticker.upper()
    articles = fetch_stock_news(ticker)
    sentiment = analyze_news_sentiment(articles)

    return {
        "ticker": ticker,
        "articles": articles,
        **sentiment,
    }


def get_ai_news_sentiment(ticker: str):
    ticker = ticker.upper()
    articles = fetch_stock_news(
        ticker=ticker,
        page_size=8,
    )
    sentiment = analyze_news_with_ai(
        ticker=ticker,
        articles=articles,
    )

    return {
        "ticker": ticker,
        **sentiment,
    }


def get_ai_market_news(
    tickers: str = "AAPL,MSFT,NVDA,GOOGL,AMZN,META,TSLA,AMD,SPY,QQQ",
):
    ticker_list = [ticker.strip().upper() for ticker in tickers.split(",")]
    results = []

    for ticker in ticker_list:
        articles = fetch_stock_news(
            ticker=ticker,
            page_size=5,
        )
        sentiment = analyze_news_with_ai(
            ticker=ticker,
            articles=articles,
        )

        results.append(
            {
                "ticker": ticker,
                **sentiment,
            }
        )

    return {
        "tracked_tickers": ticker_list,
        "results": results,
    }
