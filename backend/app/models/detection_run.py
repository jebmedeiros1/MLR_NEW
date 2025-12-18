from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, JSON, String
from sqlalchemy.orm import relationship

from app.db.base import Base


class DetectionRun(Base):
    __tablename__ = "detection_runs"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(255), nullable=False)
    status = Column(String(50), default="completed", nullable=False)
    parameters = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    anomalies = relationship("AnomalyEvent", back_populates="run", cascade="all, delete-orphan")
