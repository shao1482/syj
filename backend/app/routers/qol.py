from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.quality_of_life import QualityOfLife
from app.models.patient import Patient
from app.models.alert import Alert
from app.schemas.schemas import QolCreate, QolOut, QolUpdate
from app.services.alert_engine import check_qol_alerts

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
    db.flush()
    # 自动预警检查
    alerts = check_qol_alerts(patient_id, record, db)
    if alerts:
        db.add_all(alerts)
    db.commit()
    db.refresh(record)
    return record


@router.put("/{id}", response_model=QolOut)
def update_qol(patient_id: int, id: int, data: QolUpdate, db: Session = Depends(get_db)):
    record = db.query(QualityOfLife).filter(QualityOfLife.id == id, QualityOfLife.patient_id == patient_id).first()
    if not record:
        raise HTTPException(404, "生活质量记录不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(record, k, v)
    db.commit()
    db.refresh(record)
    return record


@router.delete("/{id}")
def delete_qol(patient_id: int, id: int, db: Session = Depends(get_db)):
    record = db.query(QualityOfLife).filter(QualityOfLife.id == id, QualityOfLife.patient_id == patient_id).first()
    if not record:
        raise HTTPException(404, "生活质量记录不存在")
    db.delete(record)
    db.commit()
    return {"message": "已删除"}