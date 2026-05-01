from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.models.alert import Alert
from app.schemas.schemas import AlertOut, AlertResolve

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("/", response_model=List[AlertOut])
def list_alerts(status: Optional[str] = None, level: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Alert).order_by(Alert.created_at.desc())
    if status:
        q = q.filter(Alert.status == status)
    if level:
        q = q.filter(Alert.level == level)
    return q.all()


@router.get("/{id}", response_model=AlertOut)
def get_alert(id: int, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == id).first()
    if not alert:
        raise HTTPException(404, "预警不存在")
    return alert


@router.put("/{id}", response_model=AlertOut)
def resolve_alert(id: int, data: AlertResolve, db: Session = Depends(get_db)):
    alert = db.query(Alert).filter(Alert.id == id).first()
    if not alert:
        raise HTTPException(404, "预警不存在")
    alert.status = data.status
    db.commit()
    db.refresh(alert)
    return alert