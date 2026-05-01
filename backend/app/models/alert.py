from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    alert_type = Column(String(50), nullable=False)  # lab / tcm / qol / followup
    level = Column(String(10), nullable=False)        # low / medium / high
    message = Column(String(500), nullable=False)
    trigger_value = Column(Float)
    threshold = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="pending")   # pending / resolved

    patient = relationship("Patient", back_populates="alerts")