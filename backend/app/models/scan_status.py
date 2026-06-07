from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.sql import func

from app.database import Base


class ScanStatus(Base):
    __tablename__ = "scan_status"

    id = Column(Integer, primary_key=True, index=True)

    scan_id = Column(String, index=True)
    market = Column(String, index=True)

    status = Column(String, default="IDLE")

    total_scanned = Column(Integer, default=0)
    opportunities_found = Column(Integer, default=0)

    duration_seconds = Column(Float, default=0)

    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())