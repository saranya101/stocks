from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func

from app.database import Base


class TradePlan(Base):
    __tablename__ = "trade_plans"

    id = Column(Integer, primary_key=True, index=True)

    ticker = Column(String, index=True, nullable=False)
    market = Column(String, default="us")

    direction = Column(String, default="LONG")
    conviction = Column(Float, default=0)
    probability = Column(Float, default=0)

    grade = Column(String)
    recommendation = Column(String)

    entry_price = Column(Float)
    stop_loss = Column(Float)
    take_profit = Column(Float)
    risk_reward = Column(Float)

    expected_hold_days = Column(Integer)
    shares = Column(Integer)
    risk_amount = Column(Float)
    risk_per_share = Column(Float)
    position_value = Column(Float)

    technical_score = Column(Float)
    backtest_score = Column(Float)
    news_score = Column(Float)
    volume_score = Column(Float)
    rsi = Column(Float)

    reasons = Column(JSON, default=[])
    raw_data = Column(JSON, default={})

    status = Column(String, default="PENDING")  
    # PENDING, APPROVED, REJECTED, SNOOZED, EXECUTED

    decision_note = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )