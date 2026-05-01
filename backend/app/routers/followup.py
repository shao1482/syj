from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import date
from app.database import get_db
from app.models.followup_plan import FollowupPlan
from app.models.patient import Patient

router = APIRouter(prefix="/api/patients/{patient_id}/followups", tags=["followups"])


class FollowupCreate(BaseModel):
    plan_date: date
    actual_date: date | None = None
    status: str = "planned"
    content: str | None = None
    symptom_change: str | None = None
    doctor_advice: str | None = None


class FollowupOut(BaseModel):
    id: int
    patient_id: int
    plan_date: date
    actual_date: date | None
    status: str
    content: str | None
    symptom_change: str | None
    doctor_advice: str | None
    created_at: str | None

    model_config = {"from_attributes": True}


@router.get("/", response_model=List[FollowupOut])
def list_followups(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(404, "患者不存在")
    return db.query(FollowupPlan).filter(FollowupPlan.patient_id == patient_id).order_by(FollowupPlan.plan_date.desc()).all()


@router.post("/", response_model=FollowupOut)
def create_followup(patient_id: int, data: FollowupCreate, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(404, "患者不存在")
    followup = FollowupPlan(patient_id=patient_id, **data.model_dump())
    db.add(followup)
    db.commit()
    db.refresh(followup)
    return followup


@router.put("/{id}", response_model=FollowupOut)
def update_followup(patient_id: int, id: int, data: FollowupCreate, db: Session = Depends(get_db)):
    followup = db.query(FollowupPlan).filter(FollowupPlan.id == id, FollowupPlan.patient_id == patient_id).first()
    if not followup:
        raise HTTPException(404, "随访计划不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(followup, k, v)
    db.commit()
    db.refresh(followup)
    return followup