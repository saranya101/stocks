from sqlalchemy import Column, Integer, String, DateTime, JSON
from datetime import datetime
from app.database import Base


class MarketScan(Base):
    __tablename__ = "market_scans"

    id = Column(Integer, primary_key=True, index=True)
    universe = Column(String, default="us_largecap")
    scan_mode = Column(String, default="fast")
    results = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)