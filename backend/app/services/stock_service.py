import pandas as pd

from app.data.market_data import fetch_stock_data
from app.data.universe import get_sp500_tickers
from app.decision.decision_engine import make_decision
from app.indicators.rsi import calculate_rsi
from app.indicators.sma import calculate_sma
from app.signals.technical_score import calculate_technical_score


def get_tickers():
    tickers_list = get_sp500_tickers()

    return {
        "count": len(tickers_list),
        "tickers": tickers_list,
    }


def get_stock_data(ticker: str):
    ticker = ticker.upper()
    stock = fetch_stock_data(ticker)

    if stock is None:
        return {"error": "No data found"}

    latest = stock.iloc[-1]

    return {
        "ticker": ticker,
        "latest_close": latest["Close"].item(),
        "latest_open": latest["Open"].item(),
        "latest_high": latest["High"].item(),
        "latest_low": latest["Low"].item(),
        "latest_volume": int(latest["Volume"].item()),
    }


def get_analysis(ticker: str):
    ticker = ticker.upper()
    stock = _fetch_stock_with_indicators(ticker)

    if stock is None:
        return {"error": "No data found"}

    latest = stock.iloc[-1]
    close = latest["Close"].item()
    sma20 = latest["SMA20"].item()
    sma50 = latest["SMA50"].item()
    rsi = latest["RSI"].item()

    score, reasons = calculate_technical_score(
        sma20=sma20,
        sma50=sma50,
        rsi=rsi,
    )
    decision = make_decision(score)

    return {
        "ticker": ticker,
        "close": close,
        "sma20": sma20,
        "sma50": sma50,
        "rsi": rsi,
        "technical_score": score,
        "decision": decision,
        "reasons": reasons,
    }


def get_scanner_results(limit: int = 25):
    tickers_list = get_sp500_tickers()[:limit]
    results = []

    for ticker in tickers_list:
        analysis = get_analysis(ticker)

        if "error" in analysis:
            continue

        results.append(
            {
                "ticker": ticker,
                "close": analysis["close"],
                "technical_score": analysis["technical_score"],
                "decision": analysis["decision"],
                "rsi": analysis["rsi"],
                "sma20": analysis["sma20"],
                "sma50": analysis["sma50"],
                "reasons": analysis["reasons"],
            }
        )

    results = sorted(
        results,
        key=lambda item: item["technical_score"],
        reverse=True,
    )

    return {
        "count": len(results),
        "results": results,
    }


def get_stock_detail(ticker: str):
    ticker = ticker.upper()
    stock = _fetch_stock_with_indicators(ticker)

    if stock is None:
        return {"error": "No data found"}

    latest = stock.iloc[-1]
    close = latest["Close"].item()
    sma20 = latest["SMA20"].item()
    sma50 = latest["SMA50"].item()
    rsi = latest["RSI"].item()

    score, reasons = calculate_technical_score(sma20, sma50, rsi)
    decision = make_decision(score)

    chart_data = []

    for _, row in stock.tail(100).iterrows():
        chart_data.append(
            {
                "date": str(row["Date"]),
                "close": row["Close"],
                "sma20": None if pd.isna(row["SMA20"]) else row["SMA20"],
                "sma50": None if pd.isna(row["SMA50"]) else row["SMA50"],
                "rsi": None if pd.isna(row["RSI"]) else row["RSI"],
            }
        )

    return {
        "ticker": ticker,
        "close": close,
        "sma20": sma20,
        "sma50": sma50,
        "rsi": rsi,
        "technical_score": score,
        "decision": decision,
        "reasons": reasons,
        "chart_data": chart_data,
    }


def _fetch_stock_with_indicators(ticker: str, period: str = "6mo"):
    stock = fetch_stock_data(ticker, period=period)

    if stock is None:
        return None

    stock["SMA20"] = calculate_sma(stock["Close"], 20)
    stock["SMA50"] = calculate_sma(stock["Close"], 50)
    stock["RSI"] = calculate_rsi(stock["Close"])

    return stock
