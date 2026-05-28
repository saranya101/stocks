import yfinance as yf

from sqlalchemy.orm import Session

from app.models.signal import Signal


def evaluate_signals(db: Session):

    signals = (
        db.query(Signal)
        .filter(Signal.evaluated == 0)
        .all()
    )

    evaluated_count = 0

    for signal in signals:

        try:

            stock = yf.download(
                signal.ticker,
                period="1d",
                interval="1m",
                progress=False
            )

            if stock.empty:
                continue

            current_price = float(
                stock["Close"].iloc[-1]
            )

            return_pct = (
                (
                    current_price
                    - signal.price
                )
                / signal.price
            ) * 100

            signal.future_price = current_price

            signal.return_pct = round(
                return_pct,
                2
            )

            if return_pct > 0:

                signal.outcome = "WIN"

            else:

                signal.outcome = "LOSS"

            signal.evaluated = 1

            evaluated_count += 1

        except Exception as e:

            print(
                f"FAILED {signal.ticker}",
                e
            )

    db.commit()

    return {
        "evaluated_signals": evaluated_count
    }