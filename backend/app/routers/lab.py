from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.lab_test import LabTest
from app.models.patient import Patient
from app.models.alert import Alert
from app.schemas.schemas import LabTestCreate, LabTestOut, LabTestUpdate
from app.services.alert_engine import check_lab_alerts, check_combined_alerts, check_tcm_lab_combined

router = APIRouter(prefix="/api/patients/{patient_id}/lab-tests", tags=["lab"])


@router.get("/", response_model=List[LabTestOut])
def list_lab_tests(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(404, "患者不存在")
    return db.query(LabTest).filter(LabTest.patient_id == patient_id).order_by(LabTest.record_date).all()


@router.post("/", response_model=LabTestOut)
def create_lab_test(patient_id: int, data: LabTestCreate, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(404, "患者不存在")
    test = LabTest(patient_id=patient_id, **data.model_dump())
    db.add(test)
    db.flush()
    # 自动预警检查
    alerts = []
    alerts.extend(check_lab_alerts(patient_id, test, db))
    alerts.extend(check_combined_alerts(patient_id, test, db))
    alerts.extend(check_tcm_lab_combined(patient_id, test, db))
    if alerts:
        db.add_all(alerts)
    db.commit()
    db.refresh(test)
    return test


@router.put("/{id}", response_model=LabTestOut)
def update_lab_test(patient_id: int, id: int, data: LabTestUpdate, db: Session = Depends(get_db)):
    test = db.query(LabTest).filter(LabTest.id == id, LabTest.patient_id == patient_id).first()
    if not test:
        raise HTTPException(404, "检验记录不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(test, k, v)
    db.commit()
    db.refresh(test)
    return test


@router.delete("/{id}")
def delete_lab_test(patient_id: int, id: int, db: Session = Depends(get_db)):
    test = db.query(LabTest).filter(LabTest.id == id, LabTest.patient_id == patient_id).first()
    if not test:
        raise HTTPException(404, "检验记录不存在")
    db.delete(test)
    db.commit()
    return {"message": "已删除"}