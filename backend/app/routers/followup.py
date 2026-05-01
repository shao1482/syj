from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, field_validator
from datetime import date, datetime, timedelta
from typing import Optional
from app.database import get_db
from app.models.followup_plan import FollowupPlan
from app.models.patient import Patient

router = APIRouter(prefix="/api", tags=["followups"])


class FollowupCreate(BaseModel):
    plan_date: date
    actual_date: Optional[date] = None
    status: Optional[str] = "planned"
    content: Optional[str] = None
    symptom_change: Optional[str] = None
    doctor_advice: Optional[str] = None

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        valid = ['planned', 'completed', 'overdue', 'cancelled']
        if v and v not in valid:
            raise ValueError(f'状态必须为: {", ".join(valid)}')
        return v


class FollowupUpdate(BaseModel):
    plan_date: Optional[date] = None
    actual_date: Optional[date] = None
    status: Optional[str] = None
    content: Optional[str] = None
    symptom_change: Optional[str] = None
    doctor_advice: Optional[str] = None

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        valid = ['planned', 'completed', 'overdue', 'cancelled']
        if v and v not in valid:
            raise ValueError(f'状态必须为: {", ".join(valid)}')
        return v


class FollowupOut(BaseModel):
    id: int
    patient_id: int
    plan_date: date
    actual_date: Optional[date] = None
    status: str
    content: Optional[str] = None
    symptom_change: Optional[str] = None
    doctor_advice: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# 患者级随访 CRUD
@router.get("/patients/{patient_id}/followups/", response_model=List[FollowupOut])
def list_followups(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(404, "患者不存在")
    return db.query(FollowupPlan).filter(FollowupPlan.patient_id == patient_id).order_by(FollowupPlan.plan_date.desc()).all()


@router.post("/patients/{patient_id}/followups/", response_model=FollowupOut)
def create_followup(patient_id: int, data: FollowupCreate, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(404, "患者不存在")
    followup = FollowupPlan(patient_id=patient_id, **data.model_dump())
    db.add(followup)
    db.commit()
    db.refresh(followup)
    return followup


@router.put("/patients/{patient_id}/followups/{id}", response_model=FollowupOut)
def update_followup(patient_id: int, id: int, data: FollowupUpdate, db: Session = Depends(get_db)):
    followup = db.query(FollowupPlan).filter(FollowupPlan.id == id, FollowupPlan.patient_id == patient_id).first()
    if not followup:
        raise HTTPException(404, "随访计划不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(followup, k, v)
    db.commit()
    db.refresh(followup)
    return followup


@router.delete("/patients/{patient_id}/followups/{id}")
def delete_followup(patient_id: int, id: int, db: Session = Depends(get_db)):
    followup = db.query(FollowupPlan).filter(FollowupPlan.id == id, FollowupPlan.patient_id == patient_id).first()
    if not followup:
        raise HTTPException(404, "随访计划不存在")
    db.delete(followup)
    db.commit()
    return {"message": "已删除"}


# 全局随访提醒
@router.get("/followups/reminders/", response_model=List[FollowupOut])
def get_followup_reminders(db: Session = Depends(get_db)):
    """返回今日随访、即将到期(3天内)、已逾期的随访计划"""
    today = date.today()
    upcoming = today + timedelta(days=3)
    return db.query(FollowupPlan).filter(
        FollowupPlan.status.in_(['planned', 'overdue']),
        FollowupPlan.plan_date <= upcoming,
    ).order_by(FollowupPlan.plan_date).all()