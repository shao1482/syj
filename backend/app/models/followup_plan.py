from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class FollowupPlan(Base):
    __tablename__ = "followup_plans"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    plan_date = Column(Date, nullable=False)           # 计划随访日期
    actual_date = Column(Date)                          # 实际随访日期
    status = Column(String(20), default="planned")      # planned / completed / overdue
    content = Column(Text)                              # 随访内容
    symptom_change = Column(Text)                       # 症状变化
    doctor_advice = Column(Text)                        # 医嘱
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", backref="followup_plans")