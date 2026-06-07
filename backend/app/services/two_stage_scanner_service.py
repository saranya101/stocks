from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import yfinance as yf

from app.engines.signal_engine import calculate_signal
from app.services.backtest_service import single_backtest
from app.services.trade_opportunity_service import (
    calculate_atr,
    generate_trade_opportunity,
)


def calculate_backtest_score(ticker):
    result = single_backtest(
        ticker=ticker,
        fast=20,
        slow=50,
        rsi_sell=80,
        stop_loss=0.05,
    )

    if result.get("error"):
        return 40

    total_return = float(result.get("total_return", 0))
    win_rate = float(result.get("win_rate", 0))
    max_drawdown = float(result.get("max_drawdown", 0))
    profit_factor = float(result.get("profit_factor", 1))

    score = 50
    score += min(total_return, 40) * 0.5
    score += (win_rate - 50) * 0.4
    score += min(max(profit_factor - 1, 0), 3) * 8
    score -= max_drawdown * 0.4

    return round(max(0, min(100, score)), 1)


def fast_scan_ticker(ticker, timeframe="5m"):
    try:
        signal = calculate_signal(
            ticker=ticker,
            timeframe=timeframe,
        )

        if not signal:
            return None

        score = signal.get(
            "technical_score",
            signal.get("confidence", 0),
        )

        # Fast quality gate
        if score < 55:
            return None

        return {
            "ticker": ticker,
            "signal": signal,
            "fast_score": score,
        }

    except Exception as error:
        print("Fast scan failed:", ticker, error)
        return None


def deep_scan_candidate(candidate):
    try:
        ticker = candidate["ticker"]
        signal = candidate["signal"]

        stock = yf.download(
            ticker,
            period="3mo",
            interval="1d",
            progress=False,
            auto_adjust=True,
            threads=False,
        )

        if stock is None or stock.empty:
            return None

        if isinstance(stock.columns, pd.MultiIndex):
            stock.columns = stock.columns.get_level_values(0)

        atr = calculate_atr(stock)
        backtest_score = calculate_backtest_score(ticker)
        news_score = 50

        opportunity = generate_trade_opportunity(
            ticker=ticker,
            current_price=signal["price"],
            atr=atr,
            technical_score=signal.get(
                "technical_score",
                signal.get("confidence", 50),
            ),
            backtest_score=backtest_score,
            news_score=news_score,
            volume_score=signal.get(
                "volume_score",
                signal.get("technical_score", 50),
            ),
        )

        opportunity["signal"] = signal["signal"]
        opportunity["rsi"] = signal["rsi"]
        opportunity["sma_fast"] = signal["sma_fast"]
        opportunity["sma_slow"] = signal["sma_slow"]
        opportunity["reasons"] = signal["reasons"]

        return opportunity

    except Exception as error:
        print("Deep scan failed:", candidate.get("ticker"), error)
        return None


def run_two_stage_scan(
    tickers,
    timeframe="5m",
    fast_workers=16,
    deep_workers=8,
    deep_limit=50,
    final_limit=20,
):
    fast_candidates = []

    with ThreadPoolExecutor(max_workers=fast_workers) as executor:
        futures = [
            executor.submit(
                fast_scan_ticker,
                ticker,
                timeframe,
            )
            for ticker in tickers
        ]

        for future in as_completed(futures):
            result = future.result()

            if result:
                fast_candidates.append(result)

    fast_candidates = sorted(
        fast_candidates,
        key=lambda item: item["fast_score"],
        reverse=True,
    )

    deep_candidates = fast_candidates[:deep_limit]

    opportunities = []

    with ThreadPoolExecutor(max_workers=deep_workers) as executor:
        futures = [
            executor.submit(
                deep_scan_candidate,
                candidate,
            )
            for candidate in deep_candidates
        ]

        for future in as_completed(futures):
            result = future.result()

            if result:
                opportunities.append(result)

    opportunities = [
        item for item in opportunities
        if item.get("recommendation") in ["STRONG BUY", "BUY", "WATCH"]
        and item.get("shares", 0) > 0
        and item.get("conviction", 0) >= 60
        and item.get("direction") == "LONG"
    ]

    opportunities = sorted(
        opportunities,
        key=lambda item: item.get("conviction", 0),
        reverse=True,
    )

    return {
        "fast_scanned": len(tickers),
        "fast_candidates": len(fast_candidates),
        "deep_scanned": len(deep_candidates),
        "opportunities": opportunities[:final_limit],
    }