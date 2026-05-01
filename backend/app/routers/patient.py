from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.patient import Patient
from app.models.tcm_score import TcmScore
from app.models.lab_test import LabTest
from app.models.quality_of_life import QualityOfLife
from app.models.treatment import Treatment
from app.models.alert import Alert
from app.models.followup_plan import FollowupPlan
from app.schemas.schemas import PatientCreate, PatientUpdate, PatientOut

router = APIRouter(prefix="/api/patients", tags=["patients"])


@router.get("/", response_model=List[PatientOut])
def list_patients(db: Session = Depends(get_db)):
    return db.query(Patient).order_by(Patient.admission_date.desc()).all()


@router.post("/", response_model=PatientOut)
def create_patient(data: PatientCreate, db: Session = Depends(get_db)):
    patient = Patient(**data.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.get("/{id}", response_model=PatientOut)
def get_patient(id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == id).first()
    if not patient:
        raise HTTPException(404, "患者不存在")
    return patient


@router.put("/{id}", response_model=PatientOut)
def update_patient(id: int, data: PatientUpdate, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == id).first()
    if not patient:
        raise HTTPException(404, "患者不存在")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(patient, k, v)
    db.commit()
    db.refresh(patient)
    return patient


@router.delete("/{id}")
def delete_patient(id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == id).first()
    if not patient:
        raise HTTPException(404, "患者不存在")
    db.delete(patient)
    db.commit()
    return {"message": "已删除"}


@router.get("/{id}/timeline/")
def patient_timeline(id: int, db: Session = Depends(get_db)):
    """临床时间轴：按时间合并展示所有临床事件"""
    patient = db.query(Patient).filter(Patient.id == id).first()
    if not patient:
        raise HTTPException(404, "患者不存在")

    events = []

    # 入院事件
    events.append({
        "date": str(patient.admission_date),
        "type": "入院",
        "title": f"{patient.name}入院",
        "detail": f"诊断: {patient.diagnosis or '未填写'} | 中医诊断: {patient.tcm_diagnosis or '未填写'}",
    })

    # 中医证候
    for s in db.query(TcmScore).filter(TcmScore.patient_id == id).order_by(TcmScore.record_date).all():
        scores = {"脾胃虚弱": s.spleen_stomach_weak, "肝胃不和": s.liver_stomachdisharmony,
                  "脾胃湿热": s.spleen_stomach_dampheat, "胃阴不足": s.stomach_yin_deficiency}
        dominant = max(scores, key=scores.get)
        events.append({
            "date": str(s.record_date), "type": "中医证候",
            "title": f"证候评分 {s.total_score}分 (主导: {dominant})",
            "detail": f"脾胃虚弱{s.spleen_stomach_weak} 肝胃不和{s.liver_stomachdisharmony} "
                      f"脾胃湿热{s.spleen_stomach_dampheat} 胃阴不足{s.stomach_yin_deficiency}",
        })

    # 实验室检验
    for t in db.query(LabTest).filter(LabTest.patient_id == id).order_by(LabTest.record_date).all():
        abnormal = []
        thresholds = {"alt": 40, "ast": 40, "hgb_low": 90, "hgb_high": 160, "wbc_low": 3.5, "wbc_high": 9.5}
        if t.alt and t.alt > 40: abnormal.append(f"ALT={t.alt}")
        if t.ast and t.ast > 40: abnormal.append(f"AST={t.ast}")
        if t.hgb and t.hgb < 90: abnormal.append(f"HGB={t.hgb}")
        tag = "异常" if abnormal else "正常"
        events.append({
            "date": str(t.record_date), "type": "实验室检验",
            "title": f"检验({t.test_type}) {tag}",
            "detail": f"WBC={t.wbc or '-'} HGB={t.hgb or '-'} ALT={t.alt or '-'} AST={t.ast or '-'} "
                      + ("异常指标: " + ", ".join(abnormal) if abnormal else ""),
        })

    # 生活质量
    for q in db.query(QualityOfLife).filter(QualityOfLife.patient_id == id).order_by(QualityOfLife.record_date).all():
        events.append({
            "date": str(q.record_date), "type": "生活质量",
            "title": f"QOL评分 {q.total_score}分",
            "detail": f"营养{q.nutrition_score} 疼痛{q.pain_score} 睡眠{q.sleep_score} "
                      f"生理{q.physical_function} 心理{q.mental_health} 社会{q.social_function}",
        })

    # 治疗方案
    for tx in db.query(Treatment).filter(Treatment.patient_id == id).order_by(Treatment.start_date).all():
        end_str = f" ~ {tx.end_date}" if tx.end_date else " (持续中)"
        events.append({
            "date": str(tx.start_date), "type": "治疗方案",
            "title": f"治疗: {tx.formula_name or '未命名'}{end_str}",
            "detail": f"西药: {tx.western_medicine or '-'} 剂量: {tx.dosage or '-'} "
                      f"疗效: {tx.effect_rating or '-'}",
        })

    # 预警
    for a in db.query(Alert).filter(Alert.patient_id == id).order_by(Alert.created_at.desc()).all():
        events.append({
            "date": str(a.created_at.date()), "type": "预警",
            "title": f"预警({a.level}): {a.message[:50]}",
            "detail": a.message,
        })

    # 随访
    for f in db.query(FollowupPlan).filter(FollowupPlan.patient_id == id).order_by(FollowupPlan.plan_date).all():
        events.append({
            "date": str(f.plan_date), "type": "随访",
            "title": f"随访({f.status})",
            "detail": f"内容: {f.content or '-'} 症状变化: {f.symptom_change or '-'}",
        })

    # 出院事件
    if patient.discharge_summary:
        events.append({
            "date": str(patient.admission_date),
            "type": "出院",
            "title": f"{patient.name}出院",
            "detail": patient.discharge_summary,
        })

    # 按日期排序
    events.sort(key=lambda e: e["date"], reverse=True)
    return {"patient_id": id, "patient_name": patient.name, "events": events}