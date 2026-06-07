from io import StringIO

import pandas as pd
import requests


def read_html_tables(url):
    response = requests.get(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
            )
        },
        timeout=15,
    )

    response.raise_for_status()

    return pd.read_html(StringIO(response.text))


def get_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

    tables = read_html_tables(url)
    df = tables[0]

    return (
        df["Symbol"]
        .astype(str)
        .str.replace(".", "-", regex=False)
        .tolist()
    )


def get_nasdaq100_tickers():
    url = "https://en.wikipedia.org/wiki/Nasdaq-100"

    tables = read_html_tables(url)

    for df in tables:
        if "Ticker" in df.columns:
            return (
                df["Ticker"]
                .astype(str)
                .str.replace(".", "-", regex=False)
                .tolist()
            )

    return []


def get_sg_etfs():
    return [
        "ES3.SI",
        "G3B.SI",
        "A35.SI",
        "MBH.SI",
        "CLR.SI",
    ]

PRIORITY_US_TICKERS = [
    "NVDA", "AMD", "AVGO", "MSFT", "AAPL", "AMZN", "GOOGL", "META", "TSLA",
    "NFLX", "PLTR", "CRM", "ORCL", "ADBE", "SMCI", "DELL", "MU", "ANET",
    "NOW", "PANW", "CRWD", "SHOP", "UBER", "COIN", "HOOD", "SOFI",
]


def get_us_etfs():
    return [
        "SPY",
        "QQQ",
        "VOO",
        "VTI",
        "IWM",
        "DIA",
        "XLK",
        "XLF",
        "XLE",
        "XLV",
    ]


def get_crypto():
    return [
        "BTC-USD",
        "ETH-USD",
        "SOL-USD",
        "BNB-USD",
        "XRP-USD",
        "ADA-USD",
    ]


def unique(items):
    result = []

    for item in items:
        if item not in result:
            result.append(item)

    return result


def get_market_universe(market: str = "us", limit: int = 50):
    market = market.lower()

    if market == "us":
        tickers = unique(
            PRIORITY_US_TICKERS
            + get_sp500_tickers()
            + get_nasdaq100_tickers()
        )

    return tickers

    if market == "sg":
        return get_sg_etfs()[:limit]

    if market == "etf":
        return unique(
            get_us_etfs()
            + get_sg_etfs()
        )[:limit]

    if market == "crypto":
        return get_crypto()[:limit]

    tickers = unique(
        get_sp500_tickers()
        + get_nasdaq100_tickers()
    )

    return tickers[:limit]