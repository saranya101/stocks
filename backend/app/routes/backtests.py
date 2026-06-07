from fastapi import APIRouter

from app.services.backtest_service import (
    compare_backtests,
    get_multi_grid_backtest,
    get_multi_ticker_backtest,
    get_portfolio_backtest,
    get_top_performers,
    grid_backtest,
    single_backtest,
)


router = APIRouter()


@router.get("/backtest/{ticker}")
def backtest(
    ticker: str,
    fast: int = 20,
    slow: int = 50,
    rsi_sell: int = 80,
    stop_loss: float = 0.05,
    start_date: str = None,
    end_date: str = None,
):
    return single_backtest(ticker, fast, slow, rsi_sell, stop_loss, start_date, end_date)


@router.get("/backtest-compare/{ticker}")
def backtest_compare(ticker: str, strategies: str = None):
    return compare_backtests(ticker, strategies)


@router.get("/backtest-grid/{ticker}")
def backtest_grid(
    ticker: str,
    fast_values: str = "5,10,20",
    slow_values: str = "20,30,50",
    rsi_values: str = "75,80",
    stop_values: str = "0.03,0.05",
):
    return grid_backtest(ticker, fast_values, slow_values, rsi_values, stop_values)


@router.get("/multi-backtest")
def multi_backtest(
    tickers: str = "AAPL,MSFT,NVDA,TSLA,AMZN,GOOGL,META,SPY,QQQ",
    fast: int = 20,
    slow: int = 30,
    rsi_sell: int = 80,
    stop_loss: float = 0.05,
):
    return get_multi_ticker_backtest(tickers, fast, slow, rsi_sell, stop_loss)


@router.get("/multi-grid-backtest")
def multi_grid_backtest(
    tickers: str = "AAPL,MSFT,NVDA,TSLA,AMZN,META,SPY,QQQ",
    fast_values: str = "5,10,20",
    slow_values: str = "20,30,50",
    rsi_values: str = "70,75,80",
    stop_values: str = "0.03,0.05",
):
    return get_multi_grid_backtest(
        tickers,
        fast_values,
        slow_values,
        rsi_values,
        stop_values,
    )


@router.get("/portfolio-backtest")
def portfolio_backtest(
    tickers: str = "AAPL,GOOGL,SPY,QQQ",
    weights: str = None,
    fast: int = 5,
    slow: int = 30,
    rsi_sell: int = 70,
    stop_loss: float = 0.03,
    starting_cash: int = 10000,
):
    return get_portfolio_backtest(
        tickers,
        weights,
        fast,
        slow,
        rsi_sell,
        stop_loss,
        starting_cash,
    )


@router.get("/top-performers")
def top_performers(
    limit: int = 50,
    fast: int = 5,
    slow: int = 30,
    rsi_sell: int = 70,
    stop_loss: float = 0.03,
):
    return get_top_performers(limit, fast, slow, rsi_sell, stop_loss)

@router.get("/backtest-heatmap/{ticker}")
def backtest_heatmap(
    ticker: str,
    fast_values: str = "5,10,15,20,25,30",
    slow_values: str = "30,40,50,60,70,100",
    rsi_values: str = "80",
    stop_values: str = "0.05",
):
    return grid_backtest(ticker, fast_values, slow_values, rsi_values, stop_values)