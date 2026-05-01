from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.tcm_score import TcmScore
from app.models.patient import Patient
from app.schemas.schemas import TcmScoreCreate, TcmScoreOut

router = APIRouter(prefix="/api/patients/{patient_id}/tcm-scores", tags=["tcm"])


@router.get("/", response_model=List[TcmScoreOut])
def list_tcm_scores(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(404, "患者不存在")
    return db.query(TcmScore).filter(TcmScore.patient_id == patient_id).order_by(TcmScore.record_date).all()


@router.post("/", response_model=TcmScoreOut)
def create_tcm_score(patient_id: int, data: TcmScoreCreate, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(404, "患者不存在")
    score = TcmScore(patient_id=patient_id, **data.model_dump())
    db.add(score)
    db.commit()
    db.refresh(score)
    return score