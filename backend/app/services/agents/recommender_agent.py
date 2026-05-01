import json
from app.services.agents.base_agent import BaseAgent
from app.services.agents.clinical_rules import TCM_SYNDROME_MAP, RISK_LEVELS, RECHECK_PLAN


class RecommenderAgent(BaseAgent):
    name = "recommender"
    description = "干预建议Agent：生成个性化随访建议、治疗方案优化、预警提示"

    def execute_rules(self, context: dict) -> dict:
        collector = context.get("collector", {}).get("rule_analysis", {})
        analyzer = context.get("analyzer", {}).get("rule_analysis", {})
        assessor = context.get("assessor", {}).get("rule_analysis", {})

        risk_level = assessor.get("risk_level", "low")
        risk_factors = assessor.get("risk_factors", [])
        alert_flags = assessor.get("alert_flags", [])
        patient_info = collector.get("patient_info", {})

        # 1. 随访频率
        followup = RISK_LEVELS.get(risk_level, {}).get("followup", "每月随访")

        # 2. 中医治疗方案优化
        tcm_series = collector.get("tcm_series", [])
        treatment_suggestions = []
        if tcm_series:
            latest = tcm_series[-1]
            scores = {"脾胃虚弱": latest["spleen_stomach_weak"], "肝胃不和": latest["liver_stomachdisharmony"],
                      "脾胃湿热": latest["spleen_stomach_dampheat"], "胃阴不足": latest["stomach_yin_deficiency"]}
            dominant = max(scores, key=scores.get)
            syndrome_info = TCM_SYNDROME_MAP.get(dominant, {})
            treatment_suggestions.append({
                "type": "中医治疗", "suggestion": f"建议加强{dominant}治疗，方剂推荐：{syndrome_info.get('formula', '对症加减')}",
                "rationale": f"当前主导证型{dominant}({scores[dominant]}分)，{syndrome_info.get('desc', '')}"
            })
            # 证型演变
            if len(tcm_series) >= 2:
                prev_scores = {"脾胃虚弱": tcm_series[-2]["spleen_stomach_weak"], "肝胃不和": tcm_series[-2]["liver_stomachdisharmony"],
                               "脾胃湿热": tcm_series[-2]["spleen_stomach_dampheat"], "胃阴不足": tcm_series[-2]["stomach_yin_deficiency"]}
                prev_dominant = max(prev_scores, key=prev_scores.get)
                if dominant != prev_dominant:
                    treatment_suggestions.append({
                        "type": "证型演变", "suggestion": f"证型从{prev_dominant}演变为{dominant}，需调整治疗方案",
                        "rationale": "证型转变提示病情动态变化"
                    })

        # 3. 饮食/生活方式建议
        lifestyle = []
        if tcm_series:
            scores = {"脾胃虚弱": tcm_series[-1]["spleen_stomach_weak"],
                      "肝胃不和": tcm_series[-1]["liver_stomachdisharmony"],
                      "脾胃湿热": tcm_series[-1]["spleen_stomach_dampheat"],
                      "胃阴不足": tcm_series[-1]["stomach_yin_deficiency"]}
            dominant = max(scores, key=scores.get)
            diet_advice = TCM_SYNDROME_MAP.get(dominant, {}).get("diet", "")
            if diet_advice:
                lifestyle.append({"category": "饮食", "advice": diet_advice})
        lifestyle.append({"category": "运动", "advice": "建议适度活动，可练习八段锦、太极拳等健脾理气功法"})
        lifestyle.append({"category": "作息", "advice": "规律作息，避免熬夜，保证充足睡眠"})

        # 4. 检验复查计划
        recheck = RECHECK_PLAN.get(risk_level, RECHECK_PLAN["low"])

        # 5. 预警提示同步
        alert_suggestions = []
        for flag in alert_flags:
            alert_suggestions.append({"source": "联合预警", "message": flag["message"], "level": flag["level"]})
        for factor in risk_factors:
            if factor.get("domain") == "实验室检验":
                alert_suggestions.append({"source": "检验异常", "message": factor["factor"], "level": "medium"})

        return {"followup_plan": {"frequency": followup, "risk_level": risk_level},
                "treatment_suggestions": treatment_suggestions,
                "lifestyle_advice": lifestyle,
                "recheck_plan": recheck,
                "alert_suggestions": alert_suggestions}

    def build_prompt(self, context, rule_result) -> str:
        assessor = context.get("assessor", {}).get("rule_analysis", {})
        collector = context.get("collector", {}).get("rule_analysis", {})
        p = collector.get("patient_info", {})
        return f"请根据以下风险评估结果，生成脾胃消化患者的个性化干预建议和随访计划：患者{p.get('name','')},{p.get('age','')}岁。风险等级：{assessor.get('risk_level_label','')}，评分：{assessor.get('risk_score',0)}。风险因素：{json.dumps(assessor.get('risk_factors',[]), ensure_ascii=False)}。"