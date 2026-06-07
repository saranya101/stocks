
import math
from unittest import result
import pandas as pd

from app.backtesting.backtester import run_backtest
from app.backtesting.portfolio_backtester import run_portfolio_backtest
from app.backtesting.risk_metrics import calculate_risk_metrics
from app.data.market_data import fetch_stock_data
from app.data.universe import get_sp500_tickers
from app.indicators.rsi import calculate_rsi
from app.indicators.sma import calculate_sma

def calculate_trade_diagnostics(trades):
    completed_trades = []

    for i in range(len(trades) - 1):
        buy = trades[i]
        sell = trades[i + 1]

        if buy.get("type") == "BUY" and sell.get("type") == "SELL":
            buy_price = safe_float(buy.get("price"))
            sell_price = safe_float(sell.get("price"))

            if buy_price == 0:
                continue

            return_pct = ((sell_price - buy_price) / buy_price) * 100

            buy_date = pd.to_datetime(buy.get("date"))
            sell_date = pd.to_datetime(sell.get("date"))
            days_held = max(1, (sell_date - buy_date).days)

            completed_trades.append({
                "return_pct": return_pct,
                "days_held": days_held,
            })

    winners = [t["return_pct"] for t in completed_trades if t["return_pct"] > 0]
    losers = [t["return_pct"] for t in completed_trades if t["return_pct"] < 0]

    total_wins = sum(winners)
    total_losses = abs(sum(losers))

    return {
        "profit_factor": safe_float(total_wins / total_losses) if total_losses else safe_float(total_wins),
        "average_days_held": safe_float(
            sum(t["days_held"] for t in completed_trades) / len(completed_trades)
        ) if completed_trades else 0,
        "largest_win": safe_float(max(winners)) if winners else 0,
        "largest_loss": safe_float(min(losers)) if losers else 0,
    }

def single_backtest(
    ticker: str,
    fast: int = 20,
    slow: int = 50,
    rsi_sell: int = 80,
    stop_loss: float = 0.05,
    start_date: str = None,
    end_date: str = None,
):
    ticker = ticker.upper()
    stock = _prepare_backtest_stock(ticker, fast, slow, start_date, end_date)

    if stock is None:
        return {
            "ticker": ticker,
            "error": "Not enough clean price data to run backtest.",
        }

    result = _run_strategy(stock, rsi_sell, stop_loss)
    diagnostics = calculate_trade_diagnostics(result.get("trades", []))
    result.update(diagnostics)

    clean_close = stock["Close"].dropna()

    if clean_close.empty or len(clean_close) < 2:
        buy_hold_return = 0.0
    else:
        first_close = safe_float(clean_close.iloc[0])
        last_close = safe_float(clean_close.iloc[-1])

        if first_close == 0:
            buy_hold_return = 0.0
        else:
            buy_hold_return = ((last_close - first_close) / first_close) * 100

    buy_hold_return = safe_float(buy_hold_return)
    alpha = safe_float(result["total_return"]) - buy_hold_return

    buy_hold_curve = []

    starting_cash = result.get("starting_cash", 10000)

    if not clean_close.empty:
        first_close = safe_float(clean_close.iloc[0])

        if first_close > 0:
            shares = starting_cash / first_close

            for idx, price in clean_close.items():
                date_value = stock.loc[idx, "Date"] if "Date" in stock.columns else idx

                buy_hold_curve.append(
                    {
                        "date": str(date_value),
                        "value": safe_float(shares * price),
                    }
                )

    response = {
        "ticker": ticker,
        "strategy": {
            "fast_sma": fast,
            "slow_sma": slow,
            "rsi_sell": rsi_sell,
            "stop_loss": stop_loss,
        },
        "buy_hold_return": safe_float(buy_hold_return),
        "alpha": safe_float(alpha),
        "buy_hold_curve": buy_hold_curve,
        **result,
    }

    return clean_json_value(response)

def safe_float(value, default=0.0):
    try:
        value = float(value)
    except Exception:
        return default

    if math.isnan(value) or math.isinf(value):
        return default

    return value

import json

def compare_backtests(ticker, strategies=None):
    if strategies:
        strategy_list = json.loads(strategies)
    else:
        strategy_list = [
            {"name": "Strategy A", "fast": 20, "slow": 50, "rsi_sell": 80, "stop_loss": 0.05},
            {"name": "Strategy B", "fast": 10, "slow": 30, "rsi_sell": 75, "stop_loss": 0.03},
        ]

    results = []

    for strategy in strategy_list:
        result = single_backtest(
            ticker,
            int(strategy["fast"]),
            int(strategy["slow"]),
            int(strategy["rsi_sell"]),
            float(strategy["stop_loss"]),
        )

        results.append({
        "name": strategy.get("name", "Strategy"),
        "strategy": strategy,
        "total_return": result.get("total_return", 0),
        "buy_hold_return": result.get("buy_hold_return", 0),
        "alpha": result.get("alpha", 0),
        "max_drawdown": result.get("max_drawdown", 0),
        "win_rate": result.get("win_rate", 0),
        "total_trades": result.get("total_trades", 0),
        "profit_factor": result.get("profit_factor", 0),
        "average_days_held": result.get("average_days_held", 0),
        "largest_win": result.get("largest_win", 0),
        "largest_loss": result.get("largest_loss", 0),
        "trades": result.get("trades", []),
        "equity_curve": result.get("equity_curve", []),
        "buy_hold_curve": result.get("buy_hold_curve", []),
    })

    return {
        "ticker": ticker.upper(),
        "results": results,
    }

def clean_json_value(value):
    if isinstance(value, dict):
        return {k: clean_json_value(v) for k, v in value.items()}

    if isinstance(value, list):
        return [clean_json_value(v) for v in value]

    try:
        if pd.isna(value):
            return 0.0
    except Exception:
        pass

    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            return 0.0

    return value

def grid_backtest(
    ticker: str,
    fast_values: str = "5,10,20",
    slow_values: str = "20,30,50",
    rsi_values: str = "75,80",
    stop_values: str = "0.03,0.05",
):
    results = []

    for strategy in _strategy_grid(fast_values, slow_values, rsi_values, stop_values):
        result = _run_ticker_strategy(ticker, strategy)

        if result:
            results.append(
                {
                    "strategy": strategy,
                    **_summarize_backtest(result),
                }
            )

    results = sorted(
        results,
        key=lambda x: (x["total_return"], -x["max_drawdown"]),
        reverse=True,
    )

    return {
        "ticker": ticker.upper(),
        "tested_strategies": len(results),
        "results": results,
    }


def get_multi_ticker_backtest(
    tickers: str = "AAPL,MSFT,NVDA,TSLA,AMZN,GOOGL,META,SPY,QQQ",
    fast: int = 20,
    slow: int = 30,
    rsi_sell: int = 80,
    stop_loss: float = 0.05,
):
    ticker_list = _parse_tickers(tickers)
    results = []

    for ticker in ticker_list:
        result = _run_ticker_strategy(
            ticker,
            {
                "fast": fast,
                "slow": slow,
                "rsi_sell": rsi_sell,
                "stop_loss": stop_loss,
            },
        )

        if result:
            results.append(
                {
                    "ticker": ticker,
                    **_summarize_backtest(result),
                }
            )

    if len(results) == 0:
        return {"error": "No backtest results"}

    average_return = sum(item["total_return"] for item in results) / len(results)
    average_drawdown = sum(item["max_drawdown"] for item in results) / len(results)
    average_win_rate = sum(item["win_rate"] for item in results) / len(results)
    profitable_count = len([item for item in results if item["total_return"] > 0])
    consistency = (profitable_count / len(results)) * 100

    results = sorted(
        results,
        key=lambda x: x["total_return"],
        reverse=True,
    )

    return {
        "strategy": {
            "fast": fast,
            "slow": slow,
            "rsi_sell": rsi_sell,
            "stop_loss": stop_loss,
        },
        "tested_tickers": len(results),
        "average_return": average_return,
        "average_drawdown": average_drawdown,
        "average_win_rate": average_win_rate,
        "consistency": consistency,
        "results": results,
    }


def get_multi_grid_backtest(
    tickers: str = "AAPL,MSFT,NVDA,TSLA,AMZN,GOOGL,META,SPY,QQQ",
    fast_values: str = "5,10,20",
    slow_values: str = "20,30,50",
    rsi_values: str = "70,75,80",
    stop_values: str = "0.03,0.05",
):
    ticker_list = _parse_tickers(tickers)
    strategy_results = []

    for strategy in _strategy_grid(fast_values, slow_values, rsi_values, stop_values):
        per_ticker_results = []

        for ticker in ticker_list:
            result = _run_ticker_strategy(ticker, strategy)

            if result:
                per_ticker_results.append(
                    {
                        "ticker": ticker,
                        "total_return": result["total_return"],
                        "max_drawdown": result["max_drawdown"],
                        "win_rate": result["win_rate"],
                        "total_trades": result["total_trades"],
                    }
                )

        if len(per_ticker_results) == 0:
            continue

        average_return = sum(
            item["total_return"] for item in per_ticker_results
        ) / len(per_ticker_results)
        average_drawdown = sum(
            item["max_drawdown"] for item in per_ticker_results
        ) / len(per_ticker_results)
        average_win_rate = sum(
            item["win_rate"] for item in per_ticker_results
        ) / len(per_ticker_results)
        profitable_count = len(
            [item for item in per_ticker_results if item["total_return"] > 0]
        )
        consistency = (profitable_count / len(per_ticker_results)) * 100
        robustness_score = average_return + consistency - average_drawdown

        strategy_results.append(
            {
                "strategy": strategy,
                "tested_tickers": len(per_ticker_results),
                "average_return": average_return,
                "average_drawdown": average_drawdown,
                "average_win_rate": average_win_rate,
                "consistency": consistency,
                "robustness_score": robustness_score,
                "results": per_ticker_results,
            }
        )

    strategy_results = sorted(
        strategy_results,
        key=lambda x: x["robustness_score"],
        reverse=True,
    )

    return {
        "tested_strategies": len(strategy_results),
        "results": strategy_results,
    }


def get_portfolio_backtest(
    tickers: str = "AAPL,GOOGL,SPY,QQQ",
    weights: str = None,
    fast: int = 5,
    slow: int = 30,
    rsi_sell: int = 70,
    stop_loss: float = 0.03,
    starting_cash: int = 10000,
):
    ticker_list = _parse_tickers(tickers)

    if weights:
        weight_list = [float(w) for w in weights.split(",")]
    else:
        weight_list = [1 / len(ticker_list)] * len(ticker_list)

    if len(weight_list) != len(ticker_list):
        return {"error": "Number of weights must match number of tickers"}

    if round(sum(weight_list), 4) != 1:
        return {"error": "Weights must add up to 1.0"}

    ticker_results = []

    for ticker in ticker_list:
        result = _run_ticker_strategy(
            ticker,
            {
                "fast": fast,
                "slow": slow,
                "rsi_sell": rsi_sell,
                "stop_loss": stop_loss,
            },
        )

        if result:
            ticker_results.append(
                {
                    "ticker": ticker,
                    "weight": weight_list[ticker_list.index(ticker)],
                    "backtest": result,
                }
            )

    if len(ticker_results) == 0:
        return {"error": "No valid portfolio results"}

    portfolio = run_portfolio_backtest(
        ticker_results=ticker_results,
        starting_cash=starting_cash,
    )
    risk_metrics = calculate_risk_metrics(portfolio["equity_curve"])

    return {
        "strategy": {
            "fast": fast,
            "slow": slow,
            "rsi_sell": rsi_sell,
            "stop_loss": stop_loss,
        },
        "tickers": ticker_list,
        **portfolio,
        "risk_metrics": risk_metrics,
    }


def get_top_performers(
    limit: int = 50,
    fast: int = 5,
    slow: int = 30,
    rsi_sell: int = 70,
    stop_loss: float = 0.03,
):
    tickers_list = get_sp500_tickers()[:limit]
    results = []

    for ticker in tickers_list:
        result = _run_ticker_strategy(
            ticker,
            {
                "fast": fast,
                "slow": slow,
                "rsi_sell": rsi_sell,
                "stop_loss": stop_loss,
            },
        )

        if result:
            results.append(
                {
                    "ticker": ticker,
                    **_summarize_backtest(result),
                }
            )

    results = sorted(
        results,
        key=lambda x: x["total_return"],
        reverse=True,
    )

    return {
        "strategy": {
            "fast": fast,
            "slow": slow,
            "rsi_sell": rsi_sell,
            "stop_loss": stop_loss,
        },
        "scanned_stocks": len(results),
        "top_performers": results,
    }


def _prepare_backtest_stock(
    ticker: str,
    fast: int,
    slow: int,
    start_date: str = None,
    end_date: str = None,
):
    stock = fetch_stock_data(ticker.upper(), period="5y")

    if stock is None or stock.empty:
        return None

    stock = stock.copy()
    if "Date" in stock.columns:
        stock["Date"] = pd.to_datetime(stock["Date"])

        if start_date:
            stock = stock[stock["Date"] >= pd.to_datetime(start_date)]

        if end_date:
            stock = stock[stock["Date"] <= pd.to_datetime(end_date)]
    
    if "Date" in stock.columns:
        stock["Date"] = pd.to_datetime(stock["Date"])
        if start_date:
            stock = stock[stock["Date"] >= pd.to_datetime(start_date)]
        if end_date:
            stock = stock[stock["Date"] <= pd.to_datetime(end_date)]

    stock["Close"] = pd.to_numeric(stock["Close"], errors="coerce")
    stock = stock.dropna(subset=["Close"])

    if stock.empty or len(stock) < slow + 5:
        return None

    stock["SMA_FAST"] = calculate_sma(stock["Close"], fast)
    stock["SMA_SLOW"] = calculate_sma(stock["Close"], slow)
    stock["RSI"] = calculate_rsi(stock["Close"])

    stock = stock.dropna(subset=["SMA_FAST", "SMA_SLOW", "RSI"])

    if stock.empty:
        return None

    return stock


def _run_strategy(stock, rsi_sell: int, stop_loss: float):
    return run_backtest(
        stock,
        fast_col="SMA_FAST",
        slow_col="SMA_SLOW",
        rsi_sell=rsi_sell,
        stop_loss=stop_loss,
    )


def _run_ticker_strategy(ticker: str, strategy: dict):
    stock = _prepare_backtest_stock(ticker, strategy["fast"], strategy["slow"])

    if stock is None:
        return None

    result = _run_strategy(stock, strategy["rsi_sell"], strategy["stop_loss"])

    clean_close = stock["Close"].dropna()

    if clean_close.empty or len(clean_close) < 2:
        buy_hold_return = 0.0
    else:
        first_close = float(clean_close.iloc[0])
        last_close = float(clean_close.iloc[-1])
        buy_hold_return = ((last_close - first_close) / first_close) * 100

    buy_hold_curve = []

    starting_cash = result.get("starting_cash", 10000)

    if not clean_close.empty:
        first_close = float(clean_close.iloc[0])

        if first_close != 0:
            for index, close in clean_close.items():
                date_value = stock.loc[index, "Date"] if "Date" in stock.columns else index

                value = starting_cash * (float(close) / first_close)

                buy_hold_curve.append({
                    "date": str(date_value),
                    "value": value,
                })

    result["buy_hold_return"] = buy_hold_return
    result["buy_hold_curve"] = buy_hold_curve

    return result

def _summarize_backtest(result: dict):
    return {
        "final_value": result["final_value"],
        "total_return": result["total_return"],
        "max_drawdown": result["max_drawdown"],
        "win_rate": result["win_rate"],
        "total_trades": result["total_trades"],
    }


def _strategy_grid(
    fast_values: str,
    slow_values: str,
    rsi_values: str,
    stop_values: str,
):
    fast_list = [int(x) for x in fast_values.split(",")]
    slow_list = [int(x) for x in slow_values.split(",")]
    rsi_list = [int(x) for x in rsi_values.split(",")]
    stop_list = [float(x) for x in stop_values.split(",")]

    for fast in fast_list:
        for slow in slow_list:
            for rsi_sell in rsi_list:
                for stop_loss in stop_list:
                    if fast >= slow:
                        continue

                    yield {
                        "fast": fast,
                        "slow": slow,
                        "rsi_sell": rsi_sell,
                        "stop_loss": stop_loss,
                    }


def _parse_tickers(tickers: str):
    return [ticker.strip().upper() for ticker in tickers.split(",")]
