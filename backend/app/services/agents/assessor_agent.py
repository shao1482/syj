import json
from app.services.agents.base_agent import BaseAgent
from app.services.agents.clinical_rules import RISK_SCORING_WEIGHTS, RISK_LEVELS, get_combined_rules


class AssessorAgent(BaseAgent):
    name = "assessor"
    description = "风险评估Agent：综合多维度判定风险等级，生成风险评分与预警标记"

    def execute_rules(self, context: dict) -> dict:
        collector = context.get("collector", {}).get("rule_analysis", {})
        analyzer = context.get("analyzer", {}).get("rule_analysis", {})
        if not collector.get("data_available"):
            return {"error": "无数据"}

        # 综合风险评分计算
        risk_score = 0
        risk_factors = []

        # TCM证候风险分(0-30)
        tcm_series = collector.get("tcm_series", [])
        if tcm_series:
            latest_tcm = tcm_series[-1]
            total = latest_tcm["total_score"]
            tcm_risk = min(total / 60 * RISK_SCORING_WEIGHTS["tcm"], RISK_SCORING_WEIGHTS["tcm"])
            risk_score += tcm_risk
            scores = {"脾胃虚弱": latest_tcm["spleen_stomach_weak"], "肝胃不和": latest_tcm["liver_stomachdisharmony"],
                      "脾胃湿热": latest_tcm["spleen_stomach_dampheat"], "胃阴不足": latest_tcm["stomach_yin_deficiency"]}
            dominant = max(scores, key=scores.get)
            risk_factors.append({"domain": "中医证候", "factor": f"主导证型：{dominant}({scores[dominant]}分)", "contribution": round(tcm_risk, 1)})
            if total > 30:
                risk_factors.append({"domain": "中医证候", "factor": "证候总分偏高(>30)", "contribution": 3})

        # Lab异常风险分(0-10)
        anomalies = analyzer.get("anomalies", [])
        lab_abnormal_count = len([a for a in anomalies if a.get("type") in ("high", "low")])
        lab_risk = min(lab_abnormal_count * 2, RISK_SCORING_WEIGHTS["lab"])
        risk_score += lab_risk
        for a in anomalies:
            if a.get("type") in ("high", "low"):
                risk_factors.append({"domain": "实验室检验", "factor": f"{a['label']}异常({a['value']})", "contribution": 2})

        # QOL风险分(0-10)
        qol_series = collector.get("qol_series", [])
        if qol_series:
            latest_qol = qol_series[-1]
            qol_total = latest_qol["total"]
            qol_risk = min((60 - qol_total) / 60 * RISK_SCORING_WEIGHTS["qol"], RISK_SCORING_WEIGHTS["qol"])
            risk_score += qol_risk
            if qol_total < 20:
                risk_factors.append({"domain": "生活质量", "factor": f"生活质量总分偏低({qol_total})", "contribution": round(qol_risk, 1)})
            low_dims = []
            for dim in ["nutrition", "pain", "sleep", "physical", "mental", "social"]:
                if latest_qol.get(dim, 10) < 4:
                    low_dims.append(dim)
            if low_dims:
                risk_factors.append({"domain": "生活质量", "factor": f"低评分维度：{','.join(low_dims)}", "contribution": 1})

        # 联合预警风险加5分
        combined_rules = get_combined_rules()
        alert_flags = []
        for rule in combined_rules:
            # 简化：基于anomaly中是否同时存在相关异常
            lab_fields_in_rule = []
            for anomaly in anomalies:
                if anomaly.get("type") in ("high", "low"):
                    lab_fields_in_rule.append(anomaly.get("field", ""))
            # ALT+AST联合
            if rule["name"] == "肝纤维化风险" and "alt" in lab_fields_in_rule:
                risk_score += 5
                alert_flags.append({"rule": rule["name"], "message": rule["message"], "level": rule["level"]})
            elif rule["name"] == "胆汁淤积倾向" and "alt" in lab_fields_in_rule:
                risk_score += 3
                alert_flags.append({"rule": rule["name"], "message": rule["message"], "level": rule["level"]})
            elif rule["name"] == "贫血合并感染" and "hgb" in lab_fields_in_rule:
                risk_score += 3
                alert_flags.append({"rule": rule["name"], "message": rule["message"], "level": rule["level"]})

        # 趋势恶化加3分
        trends = analyzer.get("trends", {})
        for key, trend in trends.items():
            if trend.get("direction") == "上升" and key.startswith("tcm"):
                risk_score += 3
                risk_factors.append({"domain": "趋势恶化", "factor": "证候总分上升趋势", "contribution": 3})

        # 风险等级判定
        risk_level = "high"
        for level, config in RISK_LEVELS.items():
            if risk_score <= config["max"]:
                risk_level = level
                break

        return {"risk_score": round(risk_score, 1), "risk_level": risk_level,
                "risk_level_label": RISK_LEVELS.get(risk_level, {}).get("label", risk_level),
                "risk_factors": risk_factors, "alert_flags": alert_flags}

    def build_prompt(self, context, rule_result) -> str:
        collector = context.get("collector", {}).get("rule_analysis", {})
        analyzer = context.get("analyzer", {}).get("rule_analysis", {})
        p = collector.get("patient_info", {})
        risk_factors = rule_result.get("risk_factors", [])
        return f"请根据以下风险因素评估脾胃消化患者的整体风险等级和发展趋势：患者{p.get('name','')},{p.get('age','')}岁,诊断:{p.get('diagnosis','')}。风险评分:{rule_result.get('risk_score',0)}。风险因素：{json.dumps(risk_factors, ensure_ascii=False)}。"