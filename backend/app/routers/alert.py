from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from app.database import get_db
from app.models.alert import Alert
from app.schemas.schemas import AlertOut, AlertResolve
from app.services.alert_config import get_alert_config, update_alert_config

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("/config")
def read_config():
    return get_alert_config()


@router.put("/config")
def write_config(config: Dict[str, Any]):
    return update_alert_config(config)


@router.get("/list", response_model=List[AlertOut])
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