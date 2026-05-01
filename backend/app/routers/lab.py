from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.lab_test import LabTest
from app.models.patient import Patient
from app.schemas.schemas import LabTestCreate, LabTestOut

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
    db.commit()
    db.refresh(test)
    return test