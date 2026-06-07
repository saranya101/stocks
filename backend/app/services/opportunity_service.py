from concurrent.futures import ThreadPoolExecutor, as_completed
import math
import pandas as pd

from app.ai.market_brain import analyze_stock_intelligence
from app.backtesting.backtester import run_backtest
from app.data.market_data import fetch_stock_data
from app.data.universe import get_sp500_tickers
from app.database import SessionLocal
from app.indicators.rsi import calculate_rsi
from app.indicators.sma import calculate_sma
from app.models import AIScanResult
from app.news.ai_news_analyzer import analyze_news_with_ai
from app.news.news_fetcher import fetch_stock_news
from app.models.market_scan import MarketScan

SCAN_STATUS = {
    "running": False,
    "current": "",
    "completed": 0,
    "total": 0,
}


def to_float(value):
    if value is None:
        return 0.0

    if isinstance(value, pd.DataFrame):
        value = value.squeeze()

    if isinstance(value, pd.Series):
        value = value.dropna()
        if value.empty:
            return 0.0
        value = value.iloc[-1]

    try:
        value = float(value.item())
    except Exception:
        try:
            value = float(value)
        except Exception:
            return 0.0

    if math.isnan(value) or math.isinf(value):
        return 0.0

    return value


def get_ai_opportunities(
    limit: int = 50,
    tickers: str = "",
    fast: int = 5,
    slow: int = 30,
    rsi_sell: int = 70,
    stop_loss: float = 0.03,
    trend_weight: float = 15,
    momentum_weight: float = 10,
    backtest_weight: float = 15,
    risk_penalty: float = 15,
    scan_mode: str = "deep",
    win_rate_weight: float = 10,
    rsi_danger_level: float = 80,
    max_drawdown_allowed: float = 20,
):
    if tickers:
        tickers_list = [
            ticker.strip().upper()
            for ticker in tickers.split(",")
            if ticker.strip()
        ]
    else:
        tickers_list = get_sp500_tickers()[:limit]

    SCAN_STATUS["running"] = True
    SCAN_STATUS["completed"] = 0
    SCAN_STATUS["total"] = len(tickers_list)
    SCAN_STATUS["current"] = ""

    opportunities = []

    def scan_one(ticker):
        return _scan_ticker_opportunity(
            ticker=ticker,
            fast=fast,
            slow=slow,
            rsi_sell=rsi_sell,
            stop_loss=stop_loss,
            trend_weight=trend_weight,
            momentum_weight=momentum_weight,
            backtest_weight=backtest_weight,
            risk_penalty=risk_penalty,
            scan_mode=scan_mode,
            win_rate_weight=win_rate_weight,
            rsi_danger_level=rsi_danger_level,
            max_drawdown_allowed=max_drawdown_allowed,
        )

    max_workers = min(8, max(1, len(tickers_list)))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(scan_one, ticker): ticker
            for ticker in tickers_list
        }

        for completed, future in enumerate(as_completed(futures), start=1):
            ticker = futures[future]

            SCAN_STATUS["current"] = ticker
            SCAN_STATUS["completed"] = completed

            try:
                scan_result = future.result()
            except Exception as e:
                print(f"{ticker} scan failed:", e)
                continue

            if scan_result is None:
                continue

            opportunities.append(scan_result)
            save_ai_scan_result(scan_result)

    opportunities = sorted(
    opportunities,
    key=lambda x: x["confidence"],
    reverse=True,
    )

    save_market_scan(
        universe="custom" if tickers else "sp500",
        scan_mode=scan_mode,
        results=opportunities,
    )

    SCAN_STATUS["running"] = False
    SCAN_STATUS["completed"] = len(tickers_list)
    SCAN_STATUS["current"] = "Complete"

    return {
        "market_scan_size": len(opportunities),
        "top_opportunities": opportunities,
    }


def save_ai_scan_result(scan_result):
    db = SessionLocal()

    try:
        db_scan = AIScanResult(
            ticker=str(scan_result["ticker"]),
            confidence=float(scan_result["confidence"]),
            signal=str(scan_result["signal"]),
            risk_level=str(scan_result["risk_level"]),
            price=float(scan_result["price"]),
            rsi=float(scan_result["rsi"]),
            backtest_return=float(scan_result["backtest_return"]),
            max_drawdown=float(scan_result["max_drawdown"]),
            win_rate=float(scan_result["win_rate"]),
        )

        db.add(db_scan)
        db.commit()

    except Exception as e:
        db.rollback()
        print("Failed to save AI scan result:", e)

    finally:
        db.close()

def save_market_scan(
    universe: str,
    scan_mode: str,
    results: list,
):
    print("SAVE MARKET SCAN CALLED")
    print("Universe:", universe)
    print("Scan mode:", scan_mode)
    print("Results count:", len(results))

    db = SessionLocal()

    try:
        scan = MarketScan(
            universe=universe,
            scan_mode=scan_mode,
            results=results,
        )

        db.add(scan)
        db.commit()

        print("MARKET SCAN SAVED SUCCESSFULLY")

    except Exception as e:
        db.rollback()
        import traceback
        print("FAILED TO SAVE MARKET SCAN")
        traceback.print_exc()

    finally:
        db.close()

def _scan_ticker_opportunity(
    ticker: str,
    fast: int,
    slow: int,
    rsi_sell: int,
    stop_loss: float,
    trend_weight: float,
    momentum_weight: float,
    backtest_weight: float,
    risk_penalty: float,
    scan_mode: str,
    win_rate_weight: float,
    rsi_danger_level: float,
    max_drawdown_allowed: float,
):
    stock = fetch_stock_data(ticker, period="1y")

    if stock is None or stock.empty:
        return None

    stock["SMA_FAST"] = calculate_sma(stock["Close"], fast)
    stock["SMA_SLOW"] = calculate_sma(stock["Close"], slow)
    stock["RSI"] = calculate_rsi(stock["Close"])

    latest = stock.iloc[-1]
    if pd.isna(latest["Close"]) or pd.isna(latest["SMA_FAST"]) or pd.isna(latest["SMA_SLOW"]) or pd.isna(latest["RSI"]):
        return None

    result = run_backtest(
        stock,
        fast_col="SMA_FAST",
        slow_col="SMA_SLOW",
        rsi_sell=rsi_sell,
        stop_loss=stop_loss,
    )

    if scan_mode == "fast":
        news_sentiment = {
            "news_score": 0,
            "news_label": "FAST SCAN",
            "news_confidence": 0,
            "relevant_articles": [],
        }

    else:
        articles = fetch_stock_news(
            ticker=ticker,
            page_size=5,
        )

        news_sentiment = analyze_news_with_ai(
            ticker=ticker,
            articles=articles,
        )

    intelligence = analyze_stock_intelligence(
        ticker=ticker,
        close=latest["Close"],
        sma_fast=latest["SMA_FAST"],
        sma_slow=latest["SMA_SLOW"],
        rsi=latest["RSI"],
        news_score=news_sentiment["news_score"],
        news_label=news_sentiment["news_label"],
        backtest_return=result["total_return"],
        max_drawdown=result["max_drawdown"],
        win_rate=result["win_rate"],
        trend_weight=trend_weight,
        momentum_weight=momentum_weight,
        backtest_weight=backtest_weight,
        risk_penalty=risk_penalty,
        win_rate_weight=win_rate_weight,
        rsi_danger_level=rsi_danger_level,
        max_drawdown_allowed=max_drawdown_allowed,
    )

    return {
    **intelligence,
    "price": to_float(latest["Close"]),
    "rsi": to_float(latest["RSI"]),
    "backtest_return": to_float(result["total_return"]),
    "max_drawdown": to_float(result["max_drawdown"]),
    "win_rate": to_float(result["win_rate"]),
    "news_score": to_float(news_sentiment["news_score"]),
    "news_label": news_sentiment["news_label"],
    "news_confidence": to_float(news_sentiment["news_confidence"]),
    "news_articles": news_sentiment["relevant_articles"],
}