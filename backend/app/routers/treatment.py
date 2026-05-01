from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.treatment import Treatment
from app.models.patient import Patient
from app.schemas.schemas import TreatmentCreate, TreatmentOut

router = APIRouter(prefix="/api/patients/{patient_id}/treatments", tags=["treatment"])


@router.get("/", response_model=List[TreatmentOut])
def list_treatments(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(404, "患者不存在")
    return db.query(Treatment).filter(Treatment.patient_id == patient_id).order_by(Treatment.start_date.desc()).all()


@router.post("/", response_model=TreatmentOut)
def create_treatment(patient_id: int, data: TreatmentCreate, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(404, "患者不存在")
    treatment = Treatment(patient_id=patient_id, **data.model_dump())
    db.add(treatment)
    db.commit()
    db.refresh(treatment)
    return treatment