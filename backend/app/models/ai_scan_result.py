from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime

from app.database import Base


class AIScanResult(Base):
    __tablename__ = "ai_scan_results"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True)
    confidence = Column(Float)
    signal = Column(String)
    risk_level = Column(String)
    price = Column(Float)
    rsi = Column(Float)
    backtest_return = Column(Float)
    max_drawdown = Column(Float)
    win_rate = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)