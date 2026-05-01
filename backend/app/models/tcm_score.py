from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class TcmScore(Base):
    __tablename__ = "tcm_scores"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    record_date = Column(Date, nullable=False)
    spleen_stomach_weak = Column(Float, default=0)       # 脾胃虚弱
    liver_stomachdisharmony = Column(Float, default=0)   # 肝胃不和
    spleen_stomach_dampheat = Column(Float, default=0)   # 脾胃湿热
    stomach_yin_deficiency = Column(Float, default=0)     # 胃阴不足
    tongue_score = Column(Float, default=0)               # 舌象评分
    pulse_score = Column(Float, default=0)                # 脉象评分
    total_score = Column(Float, default=0)                # 总分

    patient = relationship("Patient", back_populates="tcm_scores")