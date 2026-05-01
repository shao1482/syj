from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class QualityOfLife(Base):
    __tablename__ = "quality_of_life"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    record_date = Column(Date, nullable=False)
    nutrition_score = Column(Float, default=0)    # 营养状态评分
    pain_score = Column(Float, default=0)         # 疼痛评分
    sleep_score = Column(Float, default=0)        # 睡眠质量评分
    physical_function = Column(Float, default=0)  # 生理功能
    mental_health = Column(Float, default=0)      # 心理健康
    social_function = Column(Float, default=0)    # 社会功能
    total_score = Column(Float, default=0)        # 总分

    patient = relationship("Patient", back_populates="qol_records")