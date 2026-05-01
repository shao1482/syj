from app.services.agents.base_agent import BaseAgent
from sqlalchemy.orm import Session
from app.models.patient import Patient
from app.models.tcm_score import TcmScore
from app.models.lab_test import LabTest
from app.models.quality_of_life import QualityOfLife
from app.models.treatment import Treatment
from app.models.alert import Alert


class CollectorAgent(BaseAgent):
    name = "collector"
    description = "数据采集Agent：自动采集并结构化患者多源临床数据"

    def __init__(self, patient_id: int, db: Session):
        self.patient_id = patient_id
        self.db = db

    def execute_rules(self, context: dict) -> dict:
        patient = self.db.query(Patient).filter(Patient.id == self.patient_id).first()
        if not patient:
            return {"error": "患者不存在", "data_available": False}
        tcm = self.db.query(TcmScore).filter(TcmScore.patient_id == self.patient_id).order_by(TcmScore.record_date).all()
        lab = self.db.query(LabTest).filter(LabTest.patient_id == self.patient_id).order_by(LabTest.record_date).all()
        qol = self.db.query(QualityOfLife).filter(QualityOfLife.patient_id == self.patient_id).order_by(QualityOfLife.record_date).all()
        tx = self.db.query(Treatment).filter(Treatment.patient_id == self.patient_id).order_by(Treatment.start_date).all()
        alerts = self.db.query(Alert).filter(Alert.patient_id == self.patient_id).order_by(Alert.created_at.desc()).all()

        # 标准化数据包
        patient_info = {"name": patient.name, "age": patient.age, "gender": patient.gender,
                        "diagnosis": patient.diagnosis, "tcm_diagnosis": patient.tcm_diagnosis}
        tcm_series = [{"date": str(s.record_date), "spleen_stomach_weak": s.spleen_stomach_weak,
                        "liver_stomachdisharmony": s.liver_stomachdisharmony,
                        "spleen_stomach_dampheat": s.spleen_stomach_dampheat,
                        "stomach_yin_deficiency": s.stomach_yin_deficiency,
                        "tongue_score": s.tongue_score, "pulse_score": s.pulse_score,
                        "total_score": s.total_score} for s in tcm]
        lab_series = [{"date": str(t.record_date), "type": t.test_type,
                        "wbc": t.wbc, "rbc": t.rbc, "hgb": t.hgb, "plt": t.plt,
                        "alt": t.alt, "ast": t.ast, "tbil": t.tbil, "alb": t.alb} for t in lab]
        qol_series = [{"date": str(q.record_date), "nutrition": q.nutrition_score,
                        "pain": q.pain_score, "sleep": q.sleep_score,
                        "physical": q.physical_function, "mental": q.mental_health,
                        "social": q.social_function, "total": q.total_score} for q in qol]
        tx_series = [{"start": str(tx.start_date), "end": str(tx.end_date) if tx.end_date else None,
                        "formula": tx.formula_name, "western": tx.western_medicine,
                        "dosage": tx.dosage, "effect": tx.effect_rating} for tx in tx]
        alert_series = [{"type": a.alert_type, "level": a.level, "message": a.message,
                         "status": a.status, "created": str(a.created_at)} for a in alerts]

        # 完整性校验
        completeness = {
            "tcm_records": len(tcm_series), "lab_records": len(lab_series),
            "qol_records": len(qol_series), "treatment_records": len(tx_series),
            "pending_alerts": len([a for a in alerts if a.status == "pending"]),
        }
        missing = []
        if not tcm_series: missing.append("中医证候评分")
        if not lab_series: missing.append("实验室检验")
        if not qol_series: missing.append("生活质量评估")
        if not tx_series: missing.append("治疗方案")
        completeness["missing_domains"] = missing
        completeness["data_quality"] = "完整" if not missing else f"缺少{', '.join(missing)}"

        return {
            "patient_info": patient_info, "tcm_series": tcm_series,
            "lab_series": lab_series, "qol_series": qol_series,
            "treatment_series": tx_series, "alert_series": alert_series,
            "completeness": completeness, "data_available": True,
        }

    def build_prompt(self, context, rule_result) -> str:
        if not rule_result.get("data_available"):
            return ""
        p = rule_result["patient_info"]
        c = rule_result["completeness"]
        return f"请对以下脾胃消化患者数据进行完整性评估和结构化摘要：患者{p['name']},{p['age']}岁,诊断:{p['diagnosis']},中医诊断:{p['tcm_diagnosis']}。数据记录：证候{c['tcm_records']}条,检验{c['lab_records']}条,生活质量{c['qol_records']}条,治疗{c['treatment_records']}条。缺少项：{c.get('missing_domains','无')}。"