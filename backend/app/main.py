from fastapi import FastAPI
from app.data.universe import get_sp500_tickers
from app.data.market_data import fetch_stock_data
from app.indicators.sma import calculate_sma
from app.indicators.rsi import calculate_rsi
from app.signals.technical_score import calculate_technical_score
from app.decision.decision_engine import make_decision
from fastapi.middleware.cors import CORSMiddleware
from app.backtesting.backtester import run_backtest
from app.backtesting.portfolio_backtester import run_portfolio_backtest
from app.backtesting.risk_metrics import calculate_risk_metrics
from app.ai.market_brain import analyze_stock_intelligence
from app.database import engine
from app.models import Base
from app.database import SessionLocal
from app.models.ai_scan_result import AIScanResult
from app.news.news_fetcher import fetch_stock_news
from app.news.news_sentiment import analyze_news_sentiment
from app.news.ai_news_analyzer import analyze_news_with_ai
from app.news.news_fetcher import fetch_stock_news
from app.news.ai_news_analyzer import analyze_news_with_ai
from app.routes.command_center import router as command_center_router

Base.metadata.create_all(bind=engine)
import pandas as pd

app = FastAPI()
app.add_middleware(
    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Trading platform backend running"}

@app.get("/tickers")
def tickers():
    tickers_list = get_sp500_tickers()

    return {
        "count": len(tickers_list),
        "tickers": tickers_list
    }
app.include_router(command_center_router)
@app.get("/stocks/{ticker}")
def stock_data(ticker: str):

    stock = fetch_stock_data(ticker.upper())

    if stock is None:
        return {"error": "No data found"}

    latest = stock.iloc[-1]

    return {
        "ticker": ticker.upper(),

        "latest_close": latest["Close"].item(),
        "latest_open": latest["Open"].item(),
        "latest_high": latest["High"].item(),
        "latest_low": latest["Low"].item(),
        "latest_volume": int(latest["Volume"].item())
    }

@app.get("/analysis/{ticker}")
def analysis(ticker: str):

    stock = fetch_stock_data(ticker.upper())

    if stock is None:
        return {"error": "No data found"}

    stock["SMA20"] = calculate_sma(stock["Close"], 20)
    stock["SMA50"] = calculate_sma(stock["Close"], 50)
    stock["RSI"] = calculate_rsi(stock["Close"])

    latest = stock.iloc[-1]

    close = latest["Close"].item()
    sma20 = latest["SMA20"].item()
    sma50 = latest["SMA50"].item()
    rsi = latest["RSI"].item()

    score, reasons = calculate_technical_score(
        sma20=sma20,
        sma50=sma50,
        rsi=rsi
    )

    decision = make_decision(score)

    return {
        "ticker": ticker.upper(),
        "close": close,
        "sma20": sma20,
        "sma50": sma50,
        "rsi": rsi,
        "technical_score": score,
        "decision": decision,
        "reasons": reasons
    }

@app.get("/scanner")
def scanner(limit: int = 25):

    tickers_list = get_sp500_tickers()[:limit]

    results = []

    for ticker in tickers_list:

        stock = fetch_stock_data(ticker)

        if stock is None:
            continue

        stock["SMA20"] = calculate_sma(stock["Close"], 20)
        stock["SMA50"] = calculate_sma(stock["Close"], 50)
        stock["RSI"] = calculate_rsi(stock["Close"])

        latest = stock.iloc[-1]

        close = latest["Close"].item()
        sma20 = latest["SMA20"].item()
        sma50 = latest["SMA50"].item()
        rsi = latest["RSI"].item()

        score, reasons = calculate_technical_score(
            sma20=sma20,
            sma50=sma50,
            rsi=rsi
        )

        decision = make_decision(score)

        results.append({
            "ticker": ticker,
            "close": close,
            "technical_score": score,
            "decision": decision,
            "rsi": rsi,
            "sma20": sma20,
            "sma50": sma50,
            "reasons": reasons
        })

    results = sorted(
        results,
        key=lambda item: item["technical_score"],
        reverse=True
    )

    return {
        "count": len(results),
        "results": results
    }


@app.get("/stock-detail/{ticker}")
def stock_detail(ticker: str):

    stock = fetch_stock_data(ticker.upper())

    if stock is None:
        return {"error": "No data found"}

    stock["SMA20"] = calculate_sma(stock["Close"], 20)
    stock["SMA50"] = calculate_sma(stock["Close"], 50)
    stock["RSI"] = calculate_rsi(stock["Close"])

    latest = stock.iloc[-1]

    close = latest["Close"].item()
    sma20 = latest["SMA20"].item()
    sma50 = latest["SMA50"].item()
    rsi = latest["RSI"].item()

    score, reasons = calculate_technical_score(sma20, sma50, rsi)
    decision = make_decision(score)

    chart_data = []

    for _, row in stock.tail(100).iterrows():
        chart_data.append({
        "date": str(row["Date"]),
        "close": row["Close"],
        "sma20": None if pd.isna(row["SMA20"]) else row["SMA20"],
        "sma50": None if pd.isna(row["SMA50"]) else row["SMA50"],
        "rsi": None if pd.isna(row["RSI"]) else row["RSI"]
    })

    return {
        "ticker": ticker.upper(),
        "close": close,
        "sma20": sma20,
        "sma50": sma50,
        "rsi": rsi,
        "technical_score": score,
        "decision": decision,
        "reasons": reasons,
        "chart_data": chart_data
    }

@app.get("/backtest/{ticker}")
def backtest(
    ticker: str,
    fast: int = 20,
    slow: int = 50,
    rsi_sell: int = 80,
    stop_loss: float = 0.05
):
    stock = fetch_stock_data(ticker.upper(), period="1y")

    if stock is None:
        return {"error": "No data found"}

    stock["SMA_FAST"] = calculate_sma(stock["Close"], fast)
    stock["SMA_SLOW"] = calculate_sma(stock["Close"], slow)
    stock["RSI"] = calculate_rsi(stock["Close"])

    result = run_backtest(
        stock,
        fast_col="SMA_FAST",
        slow_col="SMA_SLOW",
        rsi_sell=rsi_sell,
        stop_loss=stop_loss
    )

    return {
        "ticker": ticker.upper(),
        "strategy": {
            "fast_sma": fast,
            "slow_sma": slow,
            "rsi_sell": rsi_sell,
            "stop_loss": stop_loss
        },
        **result
    }

@app.get("/backtest-compare/{ticker}")
def backtest_compare(ticker: str):

    strategies = [
        {"fast": 10, "slow": 30, "rsi_sell": 75, "stop_loss": 0.03},
        {"fast": 20, "slow": 50, "rsi_sell": 80, "stop_loss": 0.05},
        {"fast": 30, "slow": 100, "rsi_sell": 80, "stop_loss": 0.05},
        {"fast": 50, "slow": 200, "rsi_sell": 85, "stop_loss": 0.08},
        {"fast": 5, "slow": 20, "rsi_sell": 75, "stop_loss": 0.03},
    ]

    results = []

    for strategy in strategies:

        stock = fetch_stock_data(ticker.upper(), period="1y")

        if stock is None:
            continue

        stock["SMA_FAST"] = calculate_sma(stock["Close"], strategy["fast"])
        stock["SMA_SLOW"] = calculate_sma(stock["Close"], strategy["slow"])
        stock["RSI"] = calculate_rsi(stock["Close"])

        result = run_backtest(
            stock,
            fast_col="SMA_FAST",
            slow_col="SMA_SLOW",
            rsi_sell=strategy["rsi_sell"],
            stop_loss=strategy["stop_loss"]
        )

        results.append({
            "strategy": strategy,
            "final_value": result["final_value"],
            "total_return": result["total_return"],
            "max_drawdown": result["max_drawdown"],
            "win_rate": result["win_rate"],
            "total_trades": result["total_trades"]
        })

    results = sorted(
        results,
        key=lambda x: (x["total_return"], -x["max_drawdown"]),
        reverse=True
    )

    return {
        "ticker": ticker.upper(),
        "results": results
    }

@app.get("/backtest-grid/{ticker}")
def backtest_grid(
    ticker: str,
    fast_values: str = "5,10,20",
    slow_values: str = "20,30,50",
    rsi_values: str = "75,80",
    stop_values: str = "0.03,0.05"
):
    fast_list = [int(x) for x in fast_values.split(",")]
    slow_list = [int(x) for x in slow_values.split(",")]
    rsi_list = [int(x) for x in rsi_values.split(",")]
    stop_list = [float(x) for x in stop_values.split(",")]

    results = []

    for fast in fast_list:
        for slow in slow_list:
            for rsi_sell in rsi_list:
                for stop_loss in stop_list:

                    if fast >= slow:
                        continue

                    stock = fetch_stock_data(ticker.upper(), period="1y")

                    if stock is None:
                        continue

                    stock["SMA_FAST"] = calculate_sma(stock["Close"], fast)
                    stock["SMA_SLOW"] = calculate_sma(stock["Close"], slow)
                    stock["RSI"] = calculate_rsi(stock["Close"])

                    result = run_backtest(
                        stock,
                        fast_col="SMA_FAST",
                        slow_col="SMA_SLOW",
                        rsi_sell=rsi_sell,
                        stop_loss=stop_loss
                    )

                    results.append({
                        "strategy": {
                            "fast": fast,
                            "slow": slow,
                            "rsi_sell": rsi_sell,
                            "stop_loss": stop_loss
                        },
                        "final_value": result["final_value"],
                        "total_return": result["total_return"],
                        "max_drawdown": result["max_drawdown"],
                        "win_rate": result["win_rate"],
                        "total_trades": result["total_trades"]
                    })

    results = sorted(
        results,
        key=lambda x: (x["total_return"], -x["max_drawdown"]),
        reverse=True
    )

    return {
        "ticker": ticker.upper(),
        "tested_strategies": len(results),
        "results": results
    }


@app.get("/multi-backtest")
def multi_backtest(
    tickers: str = "AAPL,MSFT,NVDA,TSLA,AMZN,GOOGL,META,SPY,QQQ",
    fast: int = 20,
    slow: int = 30,
    rsi_sell: int = 80,
    stop_loss: float = 0.05
):
    ticker_list = [ticker.strip().upper() for ticker in tickers.split(",")]

    results = []

    for ticker in ticker_list:
        stock = fetch_stock_data(ticker, period="1y")

        if stock is None:
            continue

        stock["SMA_FAST"] = calculate_sma(stock["Close"], fast)
        stock["SMA_SLOW"] = calculate_sma(stock["Close"], slow)
        stock["RSI"] = calculate_rsi(stock["Close"])

        result = run_backtest(
            stock,
            fast_col="SMA_FAST",
            slow_col="SMA_SLOW",
            rsi_sell=rsi_sell,
            stop_loss=stop_loss
        )

        results.append({
            "ticker": ticker,
            "final_value": result["final_value"],
            "total_return": result["total_return"],
            "max_drawdown": result["max_drawdown"],
            "win_rate": result["win_rate"],
            "total_trades": result["total_trades"]
        })

    if len(results) == 0:
        return {"error": "No backtest results"}

    average_return = sum(item["total_return"] for item in results) / len(results)
    average_drawdown = sum(item["max_drawdown"] for item in results) / len(results)
    average_win_rate = sum(item["win_rate"] for item in results) / len(results)

    profitable_count = len([
        item for item in results
        if item["total_return"] > 0
    ])

    consistency = (profitable_count / len(results)) * 100

    results = sorted(
        results,
        key=lambda x: x["total_return"],
        reverse=True
    )

    return {
        "strategy": {
            "fast": fast,
            "slow": slow,
            "rsi_sell": rsi_sell,
            "stop_loss": stop_loss
        },
        "tested_tickers": len(results),
        "average_return": average_return,
        "average_drawdown": average_drawdown,
        "average_win_rate": average_win_rate,
        "consistency": consistency,
        "results": results
    }


@app.get("/multi-grid-backtest")
def multi_grid_backtest(
    tickers: str = "AAPL,MSFT,NVDA,TSLA,AMZN,GOOGL,META,SPY,QQQ",
    fast_values: str = "5,10,20",
    slow_values: str = "20,30,50",
    rsi_values: str = "70,75,80",
    stop_values: str = "0.03,0.05"
):
    ticker_list = [ticker.strip().upper() for ticker in tickers.split(",")]

    fast_list = [int(x) for x in fast_values.split(",")]
    slow_list = [int(x) for x in slow_values.split(",")]
    rsi_list = [int(x) for x in rsi_values.split(",")]
    stop_list = [float(x) for x in stop_values.split(",")]

    strategy_results = []

    for fast in fast_list:
        for slow in slow_list:
            for rsi_sell in rsi_list:
                for stop_loss in stop_list:

                    if fast >= slow:
                        continue

                    per_ticker_results = []

                    for ticker in ticker_list:

                        stock = fetch_stock_data(ticker, period="1y")

                        if stock is None:
                            continue

                        stock["SMA_FAST"] = calculate_sma(stock["Close"], fast)
                        stock["SMA_SLOW"] = calculate_sma(stock["Close"], slow)
                        stock["RSI"] = calculate_rsi(stock["Close"])

                        result = run_backtest(
                            stock,
                            fast_col="SMA_FAST",
                            slow_col="SMA_SLOW",
                            rsi_sell=rsi_sell,
                            stop_loss=stop_loss
                        )

                        per_ticker_results.append({
                            "ticker": ticker,
                            "total_return": result["total_return"],
                            "max_drawdown": result["max_drawdown"],
                            "win_rate": result["win_rate"],
                            "total_trades": result["total_trades"]
                        })

                    if len(per_ticker_results) == 0:
                        continue

                    average_return = sum(
                        item["total_return"]
                        for item in per_ticker_results
                    ) / len(per_ticker_results)

                    average_drawdown = sum(
                        item["max_drawdown"]
                        for item in per_ticker_results
                    ) / len(per_ticker_results)

                    average_win_rate = sum(
                        item["win_rate"]
                        for item in per_ticker_results
                    ) / len(per_ticker_results)

                    profitable_count = len([
                        item for item in per_ticker_results
                        if item["total_return"] > 0
                    ])

                    consistency = (
                        profitable_count / len(per_ticker_results)
                    ) * 100

                    robustness_score = (
                        average_return
                        + consistency
                        - average_drawdown
                    )

                    strategy_results.append({
                        "strategy": {
                            "fast": fast,
                            "slow": slow,
                            "rsi_sell": rsi_sell,
                            "stop_loss": stop_loss
                        },
                        "tested_tickers": len(per_ticker_results),
                        "average_return": average_return,
                        "average_drawdown": average_drawdown,
                        "average_win_rate": average_win_rate,
                        "consistency": consistency,
                        "robustness_score": robustness_score,
                        "results": per_ticker_results
                    })

    strategy_results = sorted(
        strategy_results,
        key=lambda x: x["robustness_score"],
        reverse=True
    )

    return {
        "tested_strategies": len(strategy_results),
        "results": strategy_results
    }


@app.get("/portfolio-backtest")
def portfolio_backtest(
    tickers: str = "AAPL,GOOGL,SPY,QQQ",
    weights: str = None,
    fast: int = 5,
    slow: int = 30,
    rsi_sell: int = 70,
    stop_loss: float = 0.03,
    starting_cash: int = 10000
):
    ticker_list = [
        ticker.strip().upper()
        for ticker in tickers.split(",")
    ]

    if weights:
        weight_list = [
            float(w)
            for w in weights.split(",")
        ]
    else:
        weight_list = [
            1 / len(ticker_list)
        ] * len(ticker_list)

    if len(weight_list) != len(ticker_list):
        return {
            "error": "Number of weights must match number of tickers"
        }

    if round(sum(weight_list), 4) != 1:
        return {
            "error": "Weights must add up to 1.0"
        }

    ticker_results = []

    for ticker in ticker_list:

        stock = fetch_stock_data(
            ticker,
            period="1y"
        )

        if stock is None:
            continue

        stock["SMA_FAST"] = calculate_sma(
            stock["Close"],
            fast
        )

        stock["SMA_SLOW"] = calculate_sma(
            stock["Close"],
            slow
        )

        stock["RSI"] = calculate_rsi(
            stock["Close"]
        )

        result = run_backtest(
            stock,
            fast_col="SMA_FAST",
            slow_col="SMA_SLOW",
            rsi_sell=rsi_sell,
            stop_loss=stop_loss
        )

        ticker_results.append({
            "ticker": ticker,
            "weight": weight_list[
                ticker_list.index(ticker)
            ],
            "backtest": result
        })

    if len(ticker_results) == 0:
        return {
            "error": "No valid portfolio results"
        }

    portfolio = run_portfolio_backtest(
        ticker_results=ticker_results,
        starting_cash=starting_cash
    )

    risk_metrics = calculate_risk_metrics(
        portfolio["equity_curve"]
    )

    return {
        "strategy": {
            "fast": fast,
            "slow": slow,
            "rsi_sell": rsi_sell,
            "stop_loss": stop_loss
        },
        "tickers": ticker_list,
        **portfolio,
        "risk_metrics": risk_metrics
    }


@app.get("/top-performers")
def top_performers(
    limit: int = 50,
    fast: int = 5,
    slow: int = 30,
    rsi_sell: int = 70,
    stop_loss: float = 0.03
):
    tickers_list = get_sp500_tickers()[:limit]

    results = []

    for ticker in tickers_list:
        stock = fetch_stock_data(ticker, period="1y")

        if stock is None:
            continue

        stock["SMA_FAST"] = calculate_sma(stock["Close"], fast)
        stock["SMA_SLOW"] = calculate_sma(stock["Close"], slow)
        stock["RSI"] = calculate_rsi(stock["Close"])

        result = run_backtest(
            stock,
            fast_col="SMA_FAST",
            slow_col="SMA_SLOW",
            rsi_sell=rsi_sell,
            stop_loss=stop_loss
        )

        results.append({
            "ticker": ticker,
            "final_value": result["final_value"],
            "total_return": result["total_return"],
            "max_drawdown": result["max_drawdown"],
            "win_rate": result["win_rate"],
            "total_trades": result["total_trades"]
        })

    results = sorted(
        results,
        key=lambda x: x["total_return"],
        reverse=True
    )

    return {
        "strategy": {
            "fast": fast,
            "slow": slow,
            "rsi_sell": rsi_sell,
            "stop_loss": stop_loss
        },
        "scanned_stocks": len(results),
        "top_performers": results
    }


@app.get("/ai-opportunities")
def ai_opportunities(
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
    win_rate_weight: float = 10,
    rsi_danger_level: float = 80,
    max_drawdown_allowed: float = 20
):

    if tickers:
        tickers_list = [
            ticker.strip().upper()
            for ticker in tickers.split(",")
        ]
    else:
        tickers_list = get_sp500_tickers()[:limit]

    opportunities = []

    for ticker in tickers_list:

        stock = fetch_stock_data(
            ticker,
            period="1y"
        )

        if stock is None:
            continue

        stock["SMA_FAST"] = calculate_sma(
            stock["Close"],
            fast
        )

        stock["SMA_SLOW"] = calculate_sma(
            stock["Close"],
            slow
        )

        stock["RSI"] = calculate_rsi(
            stock["Close"]
        )

        latest = stock.iloc[-1]

        result = run_backtest(
            stock,
            fast_col="SMA_FAST",
            slow_col="SMA_SLOW",
            rsi_sell=rsi_sell,
            stop_loss=stop_loss
        )

        articles = fetch_stock_news(
            ticker=ticker,
            page_size=5
        )

        news_sentiment = analyze_news_with_ai(
            ticker=ticker,
            articles=articles
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
            max_drawdown_allowed=max_drawdown_allowed
        )

        scan_result = {
            **intelligence,
            "price": float(latest["Close"]),
            "rsi": float(latest["RSI"]),
            "backtest_return": result["total_return"],
            "max_drawdown": result["max_drawdown"],
            "win_rate": result["win_rate"],
            "news_score": news_sentiment["news_score"],
            "news_label": news_sentiment["news_label"],
            "news_confidence": news_sentiment["news_confidence"],
            "news_articles": news_sentiment["relevant_articles"],
        }

        opportunities.append(scan_result)

        db = SessionLocal()

        try:

            db_scan = AIScanResult(
                ticker=scan_result["ticker"],
                confidence=scan_result["confidence"],
                signal=scan_result["signal"],
                risk_level=scan_result["risk_level"],
                price=scan_result["price"],
                rsi=scan_result["rsi"],
                backtest_return=scan_result["backtest_return"],
                max_drawdown=scan_result["max_drawdown"],
                win_rate=scan_result["win_rate"]
            )

            db.add(db_scan)
            db.commit()

        finally:
            db.close()

    opportunities = sorted(
        opportunities,
        key=lambda x: x["confidence"],
        reverse=True
    )

    return {
        "market_scan_size": len(opportunities),
        "top_opportunities": opportunities
    }

@app.get("/news-sentiment/{ticker}")
def news_sentiment(
    ticker: str
):

    articles = fetch_stock_news(
        ticker.upper()
    )

    sentiment = analyze_news_sentiment(
        articles
    )

    return {
        "ticker": ticker.upper(),
        "articles": articles,
        **sentiment
    }


@app.get("/ai-news-sentiment/{ticker}")
def ai_news_sentiment(ticker: str):
    articles = fetch_stock_news(
        ticker=ticker.upper(),
        page_size=8
    )

    sentiment = analyze_news_with_ai(
        ticker=ticker.upper(),
        articles=articles
    )

    return {
        "ticker": ticker.upper(),
        **sentiment
    }


@app.get("/ai-market-news")
def ai_market_news(
    tickers: str = "AAPL,MSFT,NVDA,GOOGL,AMZN,META,TSLA,AMD,SPY,QQQ"
):
    ticker_list = [
        ticker.strip().upper()
        for ticker in tickers.split(",")
    ]

    results = []

    for ticker in ticker_list:
        articles = fetch_stock_news(
            ticker=ticker,
            page_size=5
        )

        sentiment = analyze_news_with_ai(
            ticker=ticker,
            articles=articles
        )

        results.append({
            "ticker": ticker,
            **sentiment
        })

    return {
        "tracked_tickers": ticker_list,
        "results": results
    }