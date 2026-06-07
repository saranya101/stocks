from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func

from app.database import Base


class MarketOpportunity(Base):
    __tablename__ = "market_opportunities"

    id = Column(Integer, primary_key=True, index=True)

    scan_id = Column(String, index=True)
    market = Column(String, index=True)

    ticker = Column(String, index=True)
    direction = Column(String)

    conviction = Column(Float)
    probability = Column(Float)
    grade = Column(String)
    recommendation = Column(String)

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

    reasons = Column(JSON)
    raw_data = Column(JSON)

    created_at = Column(DateTime(timezone=True), server_default=func.now())