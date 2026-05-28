from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import DateTime

from datetime import datetime

from app.database import Base


class Signal(Base):

    __tablename__ = "signals"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    ticker = Column(String)

    timeframe = Column(String)

    signal = Column(String)

    confidence = Column(Float)

    price = Column(Float)

    rsi = Column(Float)

    market_session = Column(String)

    reasons = Column(String)
    outcome = Column(String, nullable=True)

    future_price = Column(Float, nullable=True)

    return_pct = Column(Float, nullable=True)

    evaluated = Column(Integer, default=0)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )