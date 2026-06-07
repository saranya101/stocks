from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.sql import func
from app.database import Base


class ScanOpportunity(Base):
    __tablename__ = "scan_opportunities"

    id = Column(Integer, primary_key=True, index=True)

    scan_id = Column(Integer, ForeignKey("scan_runs.id"))

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

    reasons = Column(JSON)
    raw_data = Column(JSON)

    created_at = Column(DateTime(timezone=True), server_default=func.now())