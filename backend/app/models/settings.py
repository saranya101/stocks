from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.database import Base


class AppSettings(Base):
    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True, index=True)

    universe = Column(String, default="us_largecap")
    scan_mode = Column(String, default="fast")
    scan_limit = Column(Integer, default=50)

    fast = Column(Integer, default=5)
    slow = Column(Integer, default=30)
    rsi_sell = Column(Integer, default=70)
    stop_loss = Column(Float, default=0.03)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)