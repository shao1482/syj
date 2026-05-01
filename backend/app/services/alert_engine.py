from sqlalchemy.orm import Session
from app.models.lab_test import LabTest
from app.models.tcm_score import TcmScore
from app.models.quality_of_life import QualityOfLife
from app.models.treatment import Treatment
from app.models.alert import Alert
from datetime import date, timedelta


# 固定阈值
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

# 多指标联合预警规则
COMBINED_RULES = [
    {
        "name": "肝纤维化风险",
        "conditions": lambda lab: (lab.alt and lab.alt > 40) and (lab.ast and lab.alt and lab.ast / lab.alt > 1),
        "message": "ALT升高 + AST/ALT>1，提示肝纤维化风险",
        "level": "high",
    },
    {
        "name": "胆汁淤积倾向",
        "conditions": lambda lab: (lab.alt and lab.alt > 40) and (lab.tbil and lab.tbil > 17.1),
        "message": "ALT升高 + TBIL升高，提示胆汁淤积倾向",
        "level": "high",
    },
    {
        "name": "贫血合并感染",
        "conditions": lambda lab: (lab.hgb and lab.hgb < 90) and (lab.wbc and lab.wbc > 9.5),
        "message": "HGB偏低 + WBC偏高，提示贫血合并感染",
        "level": "high",
    },
]


def compute_dynamic_threshold(patient_id: int, field: str, db: Session) -> float:
    """基于患者历史数据计算动态基线阈值"""
    labs = db.query(LabTest).filter(LabTest.patient_id == patient_id).order_by(LabTest.record_date).all()
    values = [getattr(l, field) for l in labs if getattr(l, field, None) is not None]
    if len(values) < 3:
        return None
    mean = sum(values) / len(values)
    return mean


def check_lab_alerts(patient_id: int, lab_test: LabTest, db: Session) -> list:
    alerts = []
    # 固定阈值检查
    for field, rule in LAB_THRESHOLDS.items():
        value = getattr(lab_test, field, None)
        if value is None:
            continue
        label = rule["label"]
        # 动态阈值：如果历史数据>=3条，用均值+20%作为上限
        dynamic_high = compute_dynamic_threshold(patient_id, field, db)
        threshold = rule.get("high", None)
        if dynamic_high and threshold:
            threshold = max(threshold, dynamic_high * 1.2)
        if threshold and value > threshold:
            msg = f"{label} 异常偏高: {value} (阈值 {threshold:.1f})"
            level = "high" if value > threshold * 1.5 else "medium"
            alert = Alert(patient_id=patient_id, alert_type="lab", level=level,
                          message=msg, trigger_value=value, threshold=threshold)
            db.add(alert)
            alerts.append(alert)
        low_threshold = rule.get("low", None)
        if low_threshold and value < low_threshold:
            msg = f"{label} 异常偏低: {value} (阈值 {low_threshold})"
            level = "high" if value < low_threshold * 0.7 else "medium"
            alert = Alert(patient_id=patient_id, alert_type="lab", level=level,
                          message=msg, trigger_value=value, threshold=low_threshold)
            db.add(alert)
            alerts.append(alert)
    return alerts


def check_combined_alerts(patient_id: int, lab_test: LabTest, db: Session) -> list:
    """多指标联合预警"""
    alerts = []
    for rule in COMBINED_RULES:
        if rule["conditions"](lab_test):
            msg = f"[联合预警] {rule['message']}"
            existing = db.query(Alert).filter(
                Alert.patient_id == patient_id,
                Alert.alert_type == "combined",
                Alert.message == msg,
                Alert.status == "pending",
            ).first()
            if not existing:
                alert = Alert(patient_id=patient_id, alert_type="combined", level=rule["level"], message=msg)
                db.add(alert)
                alerts.append(alert)
    return alerts


def check_tcm_lab_combined(patient_id: int, lab_test: LabTest, db: Session) -> list:
    """中医证型关联预警"""
    alerts = []
    latest_tcm = db.query(TcmScore).filter(
        TcmScore.patient_id == patient_id
    ).order_by(TcmScore.record_date.desc()).first()
    if not latest_tcm:
        return alerts
    # TBIL升高 + 脾胃湿热证 → 肝胆湿热预警
    if lab_test.tbil and lab_test.tbil > 17.1 and latest_tcm.spleen_stomach_dampheat > 8:
        msg = f"[证型关联] TBIL升高({lab_test.tbil}) + 脾胃湿热证加重({latest_tcm.spleen_stomach_dampheat})，提示肝胆湿热"
        alert = Alert(patient_id=patient_id, alert_type="tcm_lab", level="high", message=msg)
        db.add(alert)
        alerts.append(alert)
    # ALT升高 + 肝胃不和证 → 肝郁化火预警
    if lab_test.alt and lab_test.alt > 40 and latest_tcm.liver_stomachdisharmony > 10:
        msg = f"[证型关联] ALT升高({lab_test.alt}) + 肝胃不和证加重({latest_tcm.liver_stomachdisharmony})，提示肝郁化火"
        alert = Alert(patient_id=patient_id, alert_type="tcm_lab", level="medium", message=msg)
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
            alert = Alert(patient_id=t.patient_id, alert_type="followup", level="low", message=msg)
            db.add(alert)
            alerts.append(alert)
    return alerts


# 可配置预警规则（前端可视化配置）
ALERT_CONFIG = {
    "lab_thresholds": LAB_THRESHOLDS,
    "combined_rules": [{"name": r["name"], "message": r["message"], "level": r["level"]} for r in COMBINED_RULES],
    "tcm_change_threshold": 5,
    "qol_drop_ratio": 0.7,
    "followup_overdue_days": 30,
}


def get_alert_config():
    return ALERT_CONFIG