from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.quality_of_life import QualityOfLife
from app.models.patient import Patient
from app.schemas.schemas import QolCreate, QolOut

router = APIRouter(prefix="/api/patients/{patient_id}/qol", tags=["qol"])


@router.get("/", response_model=List[QolOut])
def list_qol(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(404, "患者不存在")
    return db.query(QualityOfLife).filter(QualityOfLife.patient_id == patient_id).order_by(QualityOfLife.record_date).all()


@router.post("/", response_model=QolOut)
def create_qol(patient_id: int, data: QolCreate, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(404, "患者不存在")
    record = QualityOfLife(patient_id=patient_id, **data.model_dump())
    db.add(record)
    db.commit()
    db.refresh(record)
    return record