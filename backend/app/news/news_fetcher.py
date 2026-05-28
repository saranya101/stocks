import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv
from newsapi import NewsApiClient

load_dotenv()

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

newsapi = NewsApiClient(api_key=NEWS_API_KEY)

COMPANY_NAMES = {
    "AAPL": "Apple",
    "MSFT": "Microsoft",
    "NVDA": "Nvidia",
    "GOOGL": "Alphabet",
    "GOOG": "Alphabet",
    "AMZN": "Amazon",
    "META": "Meta Platforms",
    "TSLA": "Tesla",
    "AMD": "Advanced Micro Devices",
    "NFLX": "Netflix",
    "SPY": "S&P 500",
    "QQQ": "Nasdaq 100",
}

SOURCE_QUALITY = {
    "Finnhub": 90,
    "SEC EDGAR": 100,
    "Reuters": 95,
    "Bloomberg": 95,
    "CNBC": 85,
    "MarketWatch": 80,
    "Barron's": 85,
    "The Wall Street Journal": 95,
    "NewsAPI": 55,
}


def get_company_name(ticker):
    return COMPANY_NAMES.get(ticker.upper(), ticker.upper())


def fetch_finnhub_news(ticker, days_back=7):
    today = datetime.utcnow().date()
    start = today - timedelta(days=days_back)

    url = "https://finnhub.io/api/v1/company-news"

    params = {
        "symbol": ticker.upper(),
        "from": str(start),
        "to": str(today),
        "token": FINNHUB_API_KEY,
    }

    response = requests.get(url, params=params, timeout=15)
    response.raise_for_status()

    articles = []

    for item in response.json()[:10]:
        articles.append({
            "ticker": ticker.upper(),
            "company": get_company_name(ticker),
            "source": item.get("source") or "Finnhub",
            "source_type": "FINNHUB",
            "source_quality": SOURCE_QUALITY.get(item.get("source"), 85),
            "title": item.get("headline") or "",
            "description": item.get("summary") or "",
            "url": item.get("url"),
            "published_at": datetime.utcfromtimestamp(
                item.get("datetime", 0)
            ).isoformat()
        })

    return articles


def fetch_newsapi_fallback(ticker, page_size=5):
    company = get_company_name(ticker)

    query = (
        f'("{ticker}" OR "{company}") '
        f'AND (stock OR shares OR earnings OR revenue OR profit OR guidance '
        f'OR analyst OR market OR forecast OR upgrade OR downgrade)'
    )

    response = newsapi.get_everything(
        q=query,
        language="en",
        sort_by="publishedAt",
        page_size=page_size,
    )

    articles = []

    for article in response.get("articles", []):
        title = article.get("title") or ""
        description = article.get("description") or ""

        text = f"{title} {description}".lower()

        junk = [
            "driver",
            "download",
            "screen reader",
            "portable",
            "tutorial",
            "how to",
        ]

        if any(word in text for word in junk):
            continue

        articles.append({
            "ticker": ticker.upper(),
            "company": company,
            "source": article["source"]["name"],
            "source_type": "NEWSAPI_FALLBACK",
            "source_quality": 55,
            "title": title,
            "description": description,
            "url": article.get("url"),
            "published_at": article.get("publishedAt"),
        })

    return articles


def deduplicate_articles(articles):
    seen = set()
    clean = []

    for article in articles:
        key = (
            article.get("title", "").lower().strip(),
            article.get("url", "")
        )

        if key in seen:
            continue

        seen.add(key)
        clean.append(article)

    return clean


def fetch_stock_news(ticker, page_size=10):
    articles = []

    try:
        articles.extend(fetch_finnhub_news(ticker))
    except Exception as e:
        print("Finnhub news error:", e)

    if len(articles) < 3:
        try:
            articles.extend(fetch_newsapi_fallback(ticker, page_size=page_size))
        except Exception as e:
            print("NewsAPI fallback error:", e)

    articles = deduplicate_articles(articles)

    return articles[:page_size]