from sqlalchemy.orm import Session
from app.models.lab_test import LabTest
from app.models.tcm_score import TcmScore
from app.models.quality_of_life import QualityOfLife
from app.models.treatment import Treatment
from app.models.alert import Alert
from datetime import date, timedelta


# 实验室指标阈值
LAB_THRESHOLDS = {
    "alt": {"high": 40, "label": "ALT"},
    "ast": {"high": 40, "label": "AST"},
    "hgb": {"low": 90, "high": 160, "label": "HGB"},
    "wbc": {"low": 3.5, "high": 9.5, "label": "WBC"},
    "plt": {"low": 100, "high": 300, "label": "PLT"},
    "tbil": {"high": 17.1, "label": "TBIL"},
    "rbc": {"low": 3.5, "high": 5.5, "label": "RBC"},
    "alb": {"low": 35, "label": "ALB"},
}


def check_lab_alerts(patient_id: int, lab_test: LabTest, db: Session) -> list:
    alerts = []
    for field, rule in LAB_THRESHOLDS.items():
        value = getattr(lab_test, field, None)
        if value is None:
            continue
        label = rule["label"]
        if "high" in rule and value > rule["high"]:
            msg = f"{label} 异常偏高: {value} (阈值 {rule['high']})"
            level = "high" if value > rule["high"] * 1.5 else "medium"
            alert = Alert(patient_id=patient_id, alert_type="lab", level=level,
                          message=msg, trigger_value=value, threshold=rule["high"])
            db.add(alert)
            alerts.append(alert)
        elif "low" in rule and value < rule["low"]:
            msg = f"{label} 异常偏低: {value} (阈值 {rule['low']})"
            level = "high" if value < rule["low"] * 0.7 else "medium"
            alert = Alert(patient_id=patient_id, alert_type="lab", level=level,
                          message=msg, trigger_value=value, threshold=rule["low"])
            db.add(alert)
            alerts.append(alert)
    return alerts


def check_tcm_alerts(patient_id: int, new_score: TcmScore, db: Session) -> list:
    alerts = []
    prev = db.query(TcmScore).filter(
        TcmScore.patient_id == patient_id,
        TcmScore.record_date < new_score.record_date
    ).order_by(TcmScore.record_date.desc()).first()
    if prev and abs(new_score.total_score - prev.total_score) > 5:
        diff = new_score.total_score - prev.total_score
        direction = "升高" if diff > 0 else "降低"
        msg = f"中医证候总分{direction} {abs(diff)} 分 (从 {prev.total_score} 到 {new_score.total_score})"
        alert = Alert(patient_id=patient_id, alert_type="tcm", level="medium",
                      message=msg, trigger_value=new_score.total_score, threshold=prev.total_score)
        db.add(alert)
        alerts.append(alert)
    return alerts


def check_qol_alerts(patient_id: int, new_qol: QualityOfLife, db: Session) -> list:
    alerts = []
    prev = db.query(QualityOfLife).filter(
        QualityOfLife.patient_id == patient_id,
        QualityOfLife.record_date < new_qol.record_date
    ).order_by(QualityOfLife.record_date.desc()).first()
    if prev and prev.total_score > 0 and new_qol.total_score < prev.total_score * 0.7:
        msg = f"生活质量评分骤降: {new_qol.total_score} (上次 {prev.total_score})"
        alert = Alert(patient_id=patient_id, alert_type="qol", level="high",
                      message=msg, trigger_value=new_qol.total_score, threshold=prev.total_score)
        db.add(alert)
        alerts.append(alert)
    return alerts


def check_followup_alerts(db: Session) -> list:
    alerts = []
    overdue_days = 30
    cutoff = date.today() - timedelta(days=overdue_days)
    treatments = db.query(Treatment).filter(
        Treatment.end_date.is_(None),
        Treatment.start_date < cutoff
    ).all()
    for t in treatments:
        msg = f"患者 {t.patient_id} 治疗方案超过 {overdue_days} 天未记录随访"
        existing = db.query(Alert).filter(
            Alert.patient_id == t.patient_id,
            Alert.alert_type == "followup",
            Alert.status == "pending"
        ).first()
        if not existing:
            alert = Alert(patient_id=t.patient_id, alert_type="followup", level="low",
                          message=msg)
            db.add(alert)
            alerts.append(alert)
    return alerts