from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from app.database import Base


class Treatment(Base):
    __tablename__ = "treatments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    formula_name = Column(String(100))    # 中药方剂名称
    formula_composition = Column(Text)     # 方剂组成
    western_medicine = Column(String(200)) # 西药名称
    dosage = Column(String(100))          # 剂量
    effect_rating = Column(Float)         # 疗效评价 1-5
    followup_note = Column(Text)          # 随访记录

    patient = relationship("Patient", back_populates="treatments")