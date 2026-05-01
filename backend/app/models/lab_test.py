from sqlalchemy import Column, Integer, Float, Date, ForeignKey, String
from sqlalchemy.orm import relationship
from app.database import Base


class LabTest(Base):
    __tablename__ = "lab_tests"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    record_date = Column(Date, nullable=False)
    test_type = Column(String(50), nullable=False)  # blood_routine / liver_func / gastric
    # 血常规
    wbc = Column(Float)
    rbc = Column(Float)
    hgb = Column(Float)
    plt = Column(Float)
    # 肝功能
    alt = Column(Float)
    ast = Column(Float)
    tbil = Column(Float)
    alb = Column(Float)
    # 胃功能
    gastrin = Column(Float)
    pepsinogen_i = Column(Float)
    pepsinogen_ii = Column(Float)
    # 其他
    other_name = Column(String(100))
    other_value = Column(Float)

    patient = relationship("Patient", back_populates="lab_tests")