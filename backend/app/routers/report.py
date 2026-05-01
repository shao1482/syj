from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.patient import Patient
from app.models.lab_test import LabTest
from app.models.tcm_score import TcmScore
from app.models.quality_of_life import QualityOfLife
from app.models.alert import Alert

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/overview")
def overview(db: Session = Depends(get_db)):
    total_patients = db.query(Patient).count()
    pending_alerts = db.query(Alert).filter(Alert.status == "pending").count()
    high_alerts = db.query(Alert).filter(Alert.level == "high", Alert.status == "pending").count()
    return {
        "total_patients": total_patients,
        "pending_alerts": pending_alerts,
        "high_alerts": high_alerts,
    }


@router.get("/trend/{patient_id}")
def patient_trend(patient_id: int, db: Session = Depends(get_db)):
    tcm_scores = db.query(TcmScore).filter(TcmScore.patient_id == patient_id).order_by(TcmScore.record_date).all()
    lab_tests = db.query(LabTest).filter(LabTest.patient_id == patient_id).order_by(LabTest.record_date).all()
    qol_records = db.query(QualityOfLife).filter(QualityOfLife.patient_id == patient_id).order_by(QualityOfLife.record_date).all()

    return {
        "tcm_scores": [
            {"date": str(s.record_date), "total_score": s.total_score} for s in tcm_scores
        ],
        "lab_tests": [
            {
                "date": str(t.record_date),
                "type": t.test_type,
                "alt": t.alt, "hgb": t.hgb, "wbc": t.wbc,
            } for t in lab_tests
        ],
        "qol": [
            {"date": str(q.record_date), "total_score": q.total_score} for q in qol_records
        ],
    }