from sqlalchemy import Column, Integer, String, Date, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    gender = Column(String(10), nullable=False)
    age = Column(Integer, nullable=False)
    phone = Column(String(20))
    admission_date = Column(Date, nullable=False)
    diagnosis = Column(String(200))
    tcm_diagnosis = Column(String(200))
    notes = Column(Text)
    allergy_history = Column(Text)          # 过敏史
    past_history = Column(Text)             # 既往史
    family_history = Column(Text)           # 家族史
    admission_assessment = Column(Text)     # 入院评估
    discharge_summary = Column(Text)        # 出院小结

    tcm_scores = relationship("TcmScore", back_populates="patient", cascade="all, delete-orphan")
    lab_tests = relationship("LabTest", back_populates="patient", cascade="all, delete-orphan")
    qol_records = relationship("QualityOfLife", back_populates="patient", cascade="all, delete-orphan")
    treatments = relationship("Treatment", back_populates="patient", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="patient", cascade="all, delete-orphan")