from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float
from sqlalchemy import DateTime

from datetime import datetime

from app.database import Base


class PaperTrade(Base):

    __tablename__ = "paper_trades"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    ticker = Column(String)

    signal = Column(String)

    entry_price = Column(Float)

    quantity = Column(Float)

    confidence = Column(Float)

    status = Column(
        String,
        default="OPEN"
    )

    pnl = Column(
        Float,
        default=0
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )
