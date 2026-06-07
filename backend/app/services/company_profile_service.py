import yfinance as yf


def format_market_cap(value):
    if not value:
        return None

    value = float(value)

    if value >= 1_000_000_000_000:
        return f"${value / 1_000_000_000_000:.2f}T"

    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f}B"

    if value >= 1_000_000:
        return f"${value / 1_000_000:.2f}M"

    return f"${value:,.0f}"


def get_company_profile(ticker: str):
    try:
        info = yf.Ticker(ticker).info

        return {
            "company_name": info.get("longName") or info.get("shortName") or ticker,
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "market_cap": format_market_cap(info.get("marketCap")),
            "country": info.get("country"),
            "website": info.get("website"),
            "description": info.get("longBusinessSummary"),
            "exchange": info.get("exchange"),
            "currency": info.get("currency"),
            "yahoo_url": f"https://finance.yahoo.com/quote/{ticker}",
        }

    except Exception:
        return {
            "company_name": ticker,
            "sector": None,
            "industry": None,
            "market_cap": None,
            "country": None,
            "website": None,
            "description": None,
            "exchange": None,
            "currency": None,
            "yahoo_url": f"https://finance.yahoo.com/quote/{ticker}",
        }