from sqlalchemy.orm import Session

from app.models.signal import Signal


def save_signal(
    db: Session,
    signal_data,
    market_session
):

    signal = Signal(

        ticker=signal_data["ticker"],

        timeframe=signal_data["timeframe"],

        signal=signal_data["signal"],

        confidence=signal_data["confidence"],

        price=signal_data["price"],

        rsi=signal_data["rsi"],

        market_session=market_session,

        reasons=", ".join(
            signal_data["reasons"]
        )
    )

    db.add(signal)

    db.commit()

    db.refresh(signal)

    return signal