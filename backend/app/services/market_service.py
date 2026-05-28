import yfinance as yf
import pandas as pd


INTERVAL_MAP = {
    "1m": "1m",
    "5m": "5m",
    "15m": "15m",
    "1h": "1h",
    "1d": "1d"
}


PERIOD_MAP = {
    "1m": "1d",
    "5m": "5d",
    "15m": "5d",
    "1h": "1mo",
    "1d": "6mo"
}


def safe_float(value):

    if isinstance(value, pd.Series):
        value = value.iloc[0]

    return float(value)


def get_live_market_data(
    ticker,
    timeframe="5m"
):

    interval = INTERVAL_MAP.get(
        timeframe,
        "5m"
    )

    period = PERIOD_MAP.get(
        timeframe,
        "5d"
    )

    stock = yf.download(
        tickers=ticker,
        period=period,
        interval=interval,
        progress=False,
        auto_adjust=True
    )

    if stock.empty:
        return None

    latest = stock.iloc[-1]

    return {
        "ticker": ticker.upper(),
        "timeframe": timeframe,
        "price": safe_float(latest["Close"]),
        "high": safe_float(latest["High"]),
        "low": safe_float(latest["Low"]),
        "volume": safe_float(latest["Volume"])
    }