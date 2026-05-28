from fastapi import APIRouter

from app.engines.market_engine import get_market_state
from app.services.market_service import get_live_market_data
from app.engines.signal_engine import calculate_signal
router = APIRouter()


@router.get("/command-center")
def command_center(
    tickers: str = "AAPL,NVDA,TSLA,MSFT",
    timeframe: str = "5m"
):

    ticker_list = [
        ticker.strip().upper()
        for ticker in tickers.split(",")
    ]

    market_state = get_market_state()

    signals = []

    for ticker in ticker_list:

        signal = calculate_signal(
            ticker=ticker,
            timeframe=timeframe
        )

        if signal:
            signals.append(signal)

    return {
        "market_state": market_state,
        "timeframe": timeframe,
        "signals": signals
    }