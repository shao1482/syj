import os, json, statistics
from datetime import date
from sqlalchemy.orm import Session
from app.models.patient import Patient
from app.models.tcm_score import TcmScore
from app.models.lab_test import LabTest
from app.models.quality_of_life import QualityOfLife
from app.models.treatment import Treatment
from app.models.alert import Alert
from app.services.alert_config import get_lab_thresholds

# Ollama 本地模型配置（可选）
OLLAMA_CONFIG = {
    "enabled": False,
    "url": "http://localhost:11434",
    "model": "qwen2.5:7b",
}

ANALYSIS_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "analysis_config.json")


def load_analysis_config():
    if os.path.exists(ANALYSIS_CONFIG_PATH):
        with open(ANALYSIS_CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"model_provider": "template", "ollama_url": "", "ollama_model": ""}


def call_local_model(prompt: str) -> str:
    """预留本地模型接口，默认模板引擎，配置Ollama后自动切换"""
    config = load_analysis_config()
    if config.get("model_provider") == "ollama" and config.get("ollama_url"):
        try:
            import requests
            resp = requests.post(
                f"{config['ollama_url']}/api/generate",
                json={"model": config.get("ollama_model", "qwen2.5:7b"), "prompt": prompt, "stream": False},
                timeout=60,
            )
            return resp.json().get("response", "")
        except Exception:
            pass
    return None


def detect_trend(values: list) -> str:
    if len(values) < 2:
        return "数据不足"
    first_half = statistics.mean(values[:len(values)//2]) if len(values)//2 > 0 else values[0]
    second_half = statistics.mean(values[len(values)//2:])
    diff_pct = ((second_half - first_half) / first_half * 100) if first_half != 0 else 0
    if diff_pct > 15:
        return "上升趋势"
    elif diff_pct < -15:
        return "下降趋势"
    else:
        return "相对稳定"


def generate_tcm_analysis(tcm_scores: list) -> dict:
    if not tcm_scores:
        return {"summary": "无中医证候评分数据", "details": []}
    latest = tcm_scores[-1]
    scores = {
        "脾胃虚弱": latest.spleen_stomach_weak,
        "肝胃不和": latest.liver_stomachdisharmony,
        "脾胃湿热": latest.spleen_stomach_dampheat,
        "胃阴不足": latest.stomach_yin_deficiency,
    }
    dominant = max(scores, key=scores.get)
    total_values = [s.total_score for s in tcm_scores]
    trend = detect_trend(total_values)
    details = []
    zhengxing_map = {
        "脾胃虚弱": "脾胃虚弱证，常见面色萎黄、纳差便溏、神疲乏力",
        "肝胃不和": "肝胃不和证，常见胃脘胀痛、嗳气反酸、情志不畅",
        "脾胃湿热": "脾胃湿热证，常见口苦口黏、脘腹痞满、舌苔黄腻",
        "胃阴不足": "胃阴不足证，常见胃脘隐痛、口干便干、舌红少苔",
    }
    details.append(f"当前主导证型：{dominant}（评分 {scores[dominant]}），{zhengxing_map.get(dominant, '')}")
    if trend == "上升趋势":
        details.append(f"证候总分呈上升趋势（最新 {latest.total_score}），病情可能加重，需关注")
    elif trend == "下降趋势":
        details.append(f"证候总分呈下降趋势（最新 {latest.total_score}），治疗有效，病情好转")
    else:
        details.append(f"证候总分相对稳定（最新 {latest.total_score}），病情无明显变化")
    if len(tcm_scores) >= 2:
        prev = tcm_scores[-2]
        change = latest.total_score - prev.total_score
        details.append(f"与上次评分相比变化 {change} 分")
    return {"summary": f"证候总分趋势：{trend}，主导证型：{dominant}", "details": details}


def generate_lab_analysis(lab_tests: list) -> dict:
    if not lab_tests:
        return {"summary": "无实验室检验数据", "details": []}
    thresholds = get_lab_thresholds()
    details = []
    latest = lab_tests[-1]
    abnormal = []
    for field, rule in thresholds.items():
        val = getattr(latest, field, None)
        if val is None:
            continue
        label = rule["label"]
        if rule.get("high") and val > rule["high"]:
            abnormal.append(f"{label} 偏高 ({val} > {rule['high']})")
        elif rule.get("low") and val < rule["low"] and rule["low"] is not None:
            abnormal.append(f"{label} 偏低 ({val} < {rule['low']})")
    if abnormal:
        details.append(f"异常指标：{', '.join(abnormal)}")
    else:
        details.append("各项指标在正常范围内")
    for field_name in ["alt", "hgb", "wbc", "tbil"]:
        values = [getattr(t, field_name) for t in lab_tests if getattr(t, field_name, None) is not None]
        if len(values) >= 2:
            trend = detect_trend(values)
            label = thresholds.get(field_name, {}).get("label", field_name)
            details.append(f"{label} 趋势：{trend}（均值 {statistics.mean(values):.1f}）")
    return {"summary": f"异常指标数 {len(abnormal)}，检验趋势分析完成", "details": details}


def generate_qol_analysis(qol_records: list) -> dict:
    if not qol_records:
        return {"summary": "无生活质量评估数据", "details": []}
    latest = qol_records[-1]
    total_values = [q.total_score for q in qol_records]
    trend = detect_trend(total_values)
    details = [f"最新生活质量总分：{latest.total_score}，趋势：{trend}"]
    dimensions = {
        "营养状态": latest.nutrition_score, "疼痛": latest.pain_score,
        "睡眠质量": latest.sleep_score, "生理功能": latest.physical_function,
        "心理健康": latest.mental_health, "社会功能": latest.social_function,
    }
    low_dims = [f"{k}({v})" for k, v in dimensions.items() if v < 4]
    if low_dims:
        details.append(f"需关注维度：{', '.join(low_dims)}（低于4分）")
    return {"summary": f"生活质量趋势：{trend}", "details": details}


def generate_treatment_analysis(treatments: list) -> dict:
    if not treatments:
        return {"summary": "无治疗方案数据", "details": []}
    latest = treatments[-1]
    details = []
    if latest.formula_name:
        details.append(f"当前方剂：{latest.formula_name}")
    if latest.western_medicine:
        details.append(f"西药：{latest.western_medicine}，剂量 {latest.dosage or '未记录'}")
    if latest.effect_rating:
        rating_desc = {1: "无效", 2: "改善不明显", 3: "部分改善", 4: "明显改善", 5: "显著改善"}
        details.append(f"疗效评价：{rating_desc.get(int(latest.effect_rating), '未评价')}({latest.effect_rating}/5)")
    return {"summary": f"治疗方案记录 {len(treatments)} 条", "details": details}


def generate_recommendations(tcm: dict, lab: dict, qol: dict) -> list:
    recs = []
    # 基于证候的建议
    if tcm.get("summary") and "脾胃虚弱" in tcm["summary"]:
        recs.append("建议加强健脾益气治疗，可考虑四君子汤/参苓白术散加减")
    if tcm.get("summary") and "肝胃不和" in tcm["summary"]:
        recs.append("建议疏肝和胃，可考虑柴胡疏肝散加减，注意情志调摄")
    if tcm.get("summary") and "脾胃湿热" in tcm["summary"]:
        recs.append("建议清热化湿，可考虑半夏泻心汤/黄连温胆汤加减，忌辛辣油腻")
    if tcm.get("summary") and "胃阴不足" in tcm["summary"]:
        recs.append("建议滋阴养胃，可考虑益胃汤/沙参麦冬汤加减，忌燥热伤阴")
    # 基于检验的建议
    if "异常指标数" in lab.get("summary", ""):
        recs.append("异常检验指标需密切监测，建议复查并评估是否需要调整治疗方案")
    # 基于生活质量的建议
    if "下降趋势" in qol.get("summary", ""):
        recs.append("生活质量下降，建议加强营养支持与心理疏导")
    if not recs:
        recs.append("目前病情稳定，建议继续当前治疗方案，定期随访")
    return recs


def generate_patient_analysis(patient_id: int, db: Session) -> dict:
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        return {"error": "患者不存在"}
    tcm = db.query(TcmScore).filter(TcmScore.patient_id == patient_id).order_by(TcmScore.record_date).all()
    lab = db.query(LabTest).filter(LabTest.patient_id == patient_id).order_by(LabTest.record_date).all()
    qol = db.query(QualityOfLife).filter(QualityOfLife.patient_id == patient_id).order_by(QualityOfLife.record_date).all()
    tx = db.query(Treatment).filter(Treatment.patient_id == patient_id).order_by(Treatment.start_date).all()
    alerts = db.query(Alert).filter(Alert.patient_id == patient_id).order_by(Alert.created_at.desc()).all()

    tcm_analysis = generate_tcm_analysis(tcm)
    lab_analysis = generate_lab_analysis(lab)
    qol_analysis = generate_qol_analysis(qol)
    tx_analysis = generate_treatment_analysis(tx)
    recommendations = generate_recommendations(tcm_analysis, lab_analysis, qol_analysis)

    # 尝试调用本地模型增强分析
    ollama_enhanced = None
    if load_analysis_config().get("model_provider") == "ollama":
        prompt = f"请根据以下脾胃消化患者数据给出中医辨证分析和治疗建议：患者{patient.name},{patient.age}岁,诊断:{patient.diagnosis},{patient.tcm_diagnosis}。证候总分趋势:{tcm_analysis['summary']}。检验:{lab_analysis['summary']}。生活质量:{qol_analysis['summary']}。"
        ollama_enhanced = call_local_model(prompt)

    return {
        "patient_name": patient.name,
        "patient_age": patient.age,
        "diagnosis": patient.diagnosis,
        "tcm_diagnosis": patient.tcm_diagnosis,
        "tcm_analysis": tcm_analysis,
        "lab_analysis": lab_analysis,
        "qol_analysis": qol_analysis,
        "treatment_analysis": tx_analysis,
        "recommendations": recommendations,
        "pending_alerts": len([a for a in alerts if a.status == "pending"]),
        "ollama_enhanced": ollama_enhanced,
        "data_summary": {
            "tcm_records": len(tcm), "lab_records": len(lab),
            "qol_records": len(qol), "treatment_records": len(tx),
        },
    }