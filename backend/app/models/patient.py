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
    allergy_history = Column(Text)
    past_history = Column(Text)
    family_history = Column(Text)
    admission_assessment = Column(Text)
    discharge_summary = Column(Text)
    # 新增临床业务字段
    patient_no = Column(String(50), default='')          # 门诊号
    inpatient_no = Column(String(50), default='')        # 住院号(可选)
    bed_no = Column(String(20), default='')              # 床号(可选)
    department = Column(String(100), default='')         # 科室(可选)
    responsible_doctor = Column(String(100), default='') # 责任医生(可选)
    responsible_nurse = Column(String(100), default='')  # 责任护士(可选)
    status = Column(String(20), default='在院')          # 在院/出院/随访中/结案/失访
    risk_level = Column(String(20))                      # low/medium/high

    tcm_scores = relationship("TcmScore", back_populates="patient", cascade="all, delete-orphan")
    lab_tests = relationship("LabTest", back_populates="patient", cascade="all, delete-orphan")
    qol_records = relationship("QualityOfLife", back_populates="patient", cascade="all, delete-orphan")
    treatments = relationship("Treatment", back_populates="patient", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="patient", cascade="all, delete-orphan")