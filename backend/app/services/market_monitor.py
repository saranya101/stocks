import time
from datetime import datetime

from app.engines.market_engine import (
    get_market_state
)
from app.database import SessionLocal

from app.services.signal_logger import (
    save_signal
)
from app.engines.signal_engine import (
    calculate_signal
)
from app.services.paper_trader import (
    create_paper_trade
)


WATCHLIST = [
    "AAPL",
    "NVDA",
    "TSLA",
    "MSFT",
    "META",
    "AMZN"
]


TIMEFRAME = "5m"

CHECK_INTERVAL_SECONDS = 60


def run_market_monitor():

    print(
        "\nAI MARKET MONITOR STARTED\n"
    )

    while True:

        market = get_market_state()

        session = market["session"]

        print(
            f"\n[{datetime.utcnow()}]"
        )

        print(
            f"MARKET SESSION: {session}"
        )

        # ONLY RUN DURING ACTIVE HOURS

        if session in [
            "MARKET_OPEN",
            "PREMARKET"
        ]:

            print(
                "\nSCANNING MARKET...\n"
            )

            signals = []
            db = SessionLocal()
            for ticker in WATCHLIST:

                try:

                    signal = calculate_signal(
                        ticker=ticker,
                        timeframe=TIMEFRAME
                    )

                    if signal:

                        signals.append(signal)
                        if (
                            signal["confidence"] >= 80
                            and signal["signal"]
                            in [
                                "VERY BULLISH",
                                "BULLISH"
                            ]
                        ):

                            create_paper_trade(
                                db=db,
                                signal_data=signal
                            )

                            print(
                                f"PAPER TRADE OPENED: {signal['ticker']}"
                            )
                        save_signal(
                            db=db,
                            signal_data=signal,
                            market_session=session
                        )

                except Exception as e:

                    print(
                        f"{ticker} ERROR:",
                        e
                    )

            # SORT BEST SIGNALS
            db.close()
            signals = sorted(
                signals,
                key=lambda x: x["confidence"],
                reverse=True
            )

            # DISPLAY

            for signal in signals:

                print(
                    f"""
{signal["ticker"]}
SIGNAL: {signal["signal"]}
CONFIDENCE: {signal["confidence"]}
PRICE: {signal["price"]}
RSI: {signal["rsi"]}
REASONS: {signal["reasons"]}
"""
                )

        else:

            print(
                "MARKET CLOSED. WAITING..."
            )

        time.sleep(
            CHECK_INTERVAL_SECONDS
        )