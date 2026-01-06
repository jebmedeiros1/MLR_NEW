from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class AnomalyEvent(Base):
    __tablename__ = "anomaly_events"

    id = Column(Integer, primary_key=True, index=True)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False, index=True)
    run_id = Column(Integer, ForeignKey("detection_runs.id"), nullable=False, index=True)
    detected_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    severity = Column(Float, nullable=False)
    message = Column(String(1024), nullable=True)
    meta = Column(JSON, nullable=True)

    tag = relationship("Tag", back_populates="anomalies")
    run = relationship("DetectionRun", back_populates="anomalies")
