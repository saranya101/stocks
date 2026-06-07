import pandas as pd
import yfinance as yf

from app.engines.market_engine import get_market_state
from app.engines.signal_engine import calculate_signal
from app.services.backtest_service import single_backtest
from app.services.market_universe_service import get_market_universe
from app.services.market_universe_service import get_market_universe
from concurrent.futures import ThreadPoolExecutor, as_completed
from app.services.trade_opportunity_service import (
    calculate_atr,
    generate_trade_opportunity,
)

def calculate_real_backtest_score(ticker):
    result = single_backtest(
        ticker=ticker,
        fast=20,
        slow=50,
        rsi_sell=80,
        stop_loss=0.05,
    )

    if result.get("error"):
        print("BACKTEST ERROR:", ticker, result.get("error"))
        return 40

    total_return = float(result.get("total_return", 0))
    alpha = float(result.get("alpha", 0))
    win_rate = float(result.get("win_rate", 0))
    max_drawdown = float(result.get("max_drawdown", 0))
    profit_factor = float(result.get("profit_factor", 1))
    total_trades = int(result.get("total_trades", 0))

    score = 0

    score += max(-25, min(35, total_return * 0.7))
    score += max(-20, min(25, alpha * 0.8))
    score += max(0, min(20, win_rate * 0.25))
    score += max(-10, min(25, (profit_factor - 1) * 30))
    score += max(0, min(15, 30 - max_drawdown))

    if total_trades < 3:
        score -= 10

    final_score = round(max(0, min(100, score)), 1)

    print(
        "BACKTEST SCORE:",
        ticker,
        final_score,
        "return:",
        total_return,
        "alpha:",
        alpha,
        "win:",
        win_rate,
        "dd:",
        max_drawdown,
        "pf:",
        profit_factor,
        "trades:",
        total_trades,
    )

    return final_score

def build_market_intelligence(
    opportunities,
    market_state,
):
    total = len(opportunities)

    bullish = len(
        [
            o for o in opportunities
            if o["direction"] == "LONG"
        ]
    )

    bearish = total - bullish

    return {
        "market_regime": (
            "RISK_ON"
            if bullish > bearish
            else "RISK_OFF"
        ),
        "bullish_setups": bullish,
        "bearish_setups": bearish,
        "total_scanned": total,
        "session": market_state["session"],
    }

def build_todays_decision(
    opportunities,
):
    if not opportunities:
        return None

    best = opportunities[0]

    return {
        "ticker": best["ticker"],
        "direction": best["direction"],
        "conviction": best["conviction"],
        "probability": best["probability"],
        "entry_price": best["entry_price"],
        "stop_loss": best["stop_loss"],
        "take_profit": best["take_profit"],
        "recommendation": best["recommendation"],
    }

def build_pipeline(
    opportunities,
):
    ready = [
        o for o in opportunities
        if o["recommendation"] == "BUY"
    ]

    watch = [
        o for o in opportunities
        if o["recommendation"] == "WATCH"
    ]

    rejected = [
        o for o in opportunities
        if o["recommendation"] == "AVOID"
    ]

    return {
        "ready_count": len(ready),
        "watch_count": len(watch),
        "rejected_count": len(rejected),
    }


def build_ai_journal(
    opportunities,
):
    journal = []

    for opportunity in opportunities[:10]:

        journal.append(
            {
                "ticker": opportunity["ticker"],
                "decision": opportunity["recommendation"],
                "reason": (
                    opportunity["reasons"][0]
                    if opportunity["reasons"]
                    else "No reason"
                ),
            }
        )

    return journal


def get_command_center(
    market: str = "us",
    limit: int = 200,
    timeframe: str = "5m",
):
    ticker_list = get_market_universe(
        market=market,
        limit=limit,
    )

    if not ticker_list:
        market_state = get_market_state()

        return {
            "market_state": market_state,
            "timeframe": timeframe,
            "market_intelligence": build_market_intelligence([], market_state),
            "todays_decision": None,
            "pipeline": build_pipeline([]),
            "opportunities": [],
            "signals": [],
            "ai_journal": [],
            "error": "No market tickers found.",
        }

    market_state = get_market_state()

    def analyze_ticker(ticker, timeframe):
        try:
            signal = calculate_signal(
                ticker=ticker,
                timeframe=timeframe,
            )

            if not signal:
                return None

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

            backtest_score = calculate_real_backtest_score(ticker)

            news_score = 50

            opportunity = generate_trade_opportunity(
    ticker=ticker,
    current_price=signal["price"],
    atr=atr,
    technical_score=signal.get("technical_score", signal.get("confidence", 50)),
    backtest_score=backtest_score,
    news_score=news_score,
    volume_score=signal.get("volume_score", signal.get("technical_score", 50)),
    rsi=signal.get("rsi"),
)

            opportunity["signal"] = signal["signal"]
            opportunity["rsi"] = signal["rsi"]
            opportunity["sma_fast"] = signal["sma_fast"]
            opportunity["sma_slow"] = signal["sma_slow"]
            opportunity["reasons"] = signal["reasons"]

            return opportunity

        except Exception as error:
            print("Analyze failed:", ticker, error)
            return None

    tickers_to_scan = ticker_list[:limit]

    opportunities = []

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [
            executor.submit(
                analyze_ticker,
                ticker,
                timeframe,
            )
            for ticker in tickers_to_scan
        ]

        for future in as_completed(futures):
            result = future.result()

            if result:
                opportunities.append(result)

    opportunities = sorted(
        opportunities,
        key=lambda item: item["conviction"],
        reverse=True,
    )

    top_opportunities = opportunities[:20]

    return {
        "market_state": market_state,
        "timeframe": timeframe,

        "market_intelligence": build_market_intelligence(
            opportunities,
            market_state,
        ),

        "todays_decision": build_todays_decision(
            top_opportunities,
        ),

        "pipeline": build_pipeline(
            opportunities,
        ),

        "opportunities": top_opportunities,
        "signals": top_opportunities,

        "ai_journal": build_ai_journal(
            top_opportunities,
        ),
    }