from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func

from app.database import Base


class TradeOpportunity(Base):
    __tablename__ = "trade_opportunities"

    id = Column(Integer, primary_key=True, index=True)

    ticker = Column(String, index=True)

    direction = Column(String)

    conviction = Column(Float)

    entry_price = Column(Float)

    stop_loss = Column(Float)

    take_profit = Column(Float)

    risk_reward = Column(Float)

    expected_hold_days = Column(Integer)

    status = Column(String)

    technical_score = Column(Float)
    backtest_score = Column(Float)
    news_score = Column(Float)
    volume_score = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())