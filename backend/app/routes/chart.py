from fastapi import APIRouter
import pandas as pd
import yfinance as yf
import math
router = APIRouter()


def safe_float(value):
    if value is None:
        return None

    if isinstance(value, pd.DataFrame):
        value = value.squeeze()

    if isinstance(value, pd.Series):
        value = value.dropna()
        if value.empty:
            return None
        value = value.iloc[-1]

    try:
        value = value.item()
    except Exception:
        pass

    try:
        number = float(value)

    except Exception:
        return None

    if math.isnan(number) or math.isinf(number):
        return None

    return number


@router.get("/stock-chart/{ticker}")
def stock_chart(
    ticker: str,
    period: str = "1mo"
):
    data = yf.download(
        ticker.upper(),
        period=period,
        progress=False,
        auto_adjust=True
    )

    if data is None or data.empty:
        return {
            "ticker": ticker.upper(),
            "prices": []
        }

    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
        data["SMA20"] = data["Close"].rolling(20).mean()
        data["SMA50"] = data["Close"].rolling(50).mean()
    prices = []

    for index, row in data.iterrows():
        prices.append({
            "date": str(index.date()),
            "open": safe_float(row["Open"]),
            "high": safe_float(row["High"]),
            "low": safe_float(row["Low"]),
            "sma20": safe_float(row["SMA20"]),
            "sma50": safe_float(row["SMA50"]),
            "close": safe_float(row["Close"]),
            "volume": safe_float(row["Volume"]),
        })

    return {
        "ticker": ticker.upper(),
        "period": period,
        "prices": prices
    }