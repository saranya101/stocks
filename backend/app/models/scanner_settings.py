from sqlalchemy import Column, Integer, Boolean, DateTime
from sqlalchemy.sql import func

from app.database import Base


class ScannerSettings(Base):
    __tablename__ = "scanner_settings"

    id = Column(Integer, primary_key=True, index=True)

    enabled = Column(Boolean, default=True)
    scan_interval_minutes = Column(Integer, default=15)

    scan_us = Column(Boolean, default=True)
    scan_sg = Column(Boolean, default=False)
    scan_etf = Column(Boolean, default=True)
    scan_crypto = Column(Boolean, default=False)

    max_tickers_per_market = Column(Integer, default=200)
    max_results_per_market = Column(Integer, default=20)

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )