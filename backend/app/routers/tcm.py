from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.tcm_score import TcmScore
from app.models.patient import Patient
from app.models.alert import Alert
from app.schemas.schemas import TcmScoreCreate, TcmScoreOut, TcmScoreUpdate
from app.services.alert_engine import check_tcm_alerts

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
    db.flush()
    # 自动预警检查
    alerts = check_tcm_alerts(patient_id, score, db)
    if alerts:
        db.add_all(alerts)
    db.commit()
    db.refresh(score)
    return score


@router.put("/{id}", response_model=TcmScoreOut)
def update_tcm_score(patient_id: int, id: int, data: TcmScoreUpdate, db: Session = Depends(get_db)):
    score = db.query(TcmScore).filter(TcmScore.id == id, TcmScore.patient_id == patient_id).first()
    if not score:
        raise HTTPException(404, "证候评分记录不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(score, k, v)
    db.commit()
    db.refresh(score)
    return score


@router.delete("/{id}")
def delete_tcm_score(patient_id: int, id: int, db: Session = Depends(get_db)):
    score = db.query(TcmScore).filter(TcmScore.id == id, TcmScore.patient_id == patient_id).first()
    if not score:
        raise HTTPException(404, "证候评分记录不存在")
    db.delete(score)
    db.commit()
    return {"message": "已删除"}