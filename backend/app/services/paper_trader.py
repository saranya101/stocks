from sqlalchemy.orm import Session

from app.models.paper_trade import (
    PaperTrade
)


def create_paper_trade(
    db: Session,
    signal_data
):

    trade = PaperTrade(

        ticker=signal_data["ticker"],

        signal=signal_data["signal"],

        entry_price=signal_data["price"],

        quantity=1,

        confidence=signal_data["confidence"]
    )

    db.add(trade)

    db.commit()

    db.refresh(trade)

    return trade