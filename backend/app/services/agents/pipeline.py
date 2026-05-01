import logging
from app.services.agents.collector_agent import CollectorAgent
from app.services.agents.analyzer_agent import AnalyzerAgent
from app.services.agents.assessor_agent import AssessorAgent
from app.services.agents.recommender_agent import RecommenderAgent

logger = logging.getLogger(__name__)


class AnalysisPipeline:
    """4-Agent协作流水线：采集→解析→评估→建议 + 闭环验证"""

    def __init__(self, patient_id: int, db):
        self.patient_id = patient_id
        self.db = db
        self.agents = [
            CollectorAgent(patient_id, db),
            AnalyzerAgent(),
            AssessorAgent(),
            RecommenderAgent(),
        ]

    def run(self) -> dict:
        context = {}
        pipeline_steps = []

        for agent in self.agents:
            try:
                result = agent.run(context)
                context[agent.name] = result
                pipeline_steps.append({
                    "agent": agent.name,
                    "description": agent.description,
                    "status": "success",
                    "confidence": result.get("confidence", 0),
                })
                logger.info(f"Agent {agent.name} completed, confidence={result.get('confidence', 0)}")
            except Exception as e:
                context[agent.name] = {"error": str(e), "agent": agent.name}
                pipeline_steps.append({
                    "agent": agent.name,
                    "description": agent.description,
                    "status": "error",
                    "error": str(e),
                })
                logger.error(f"Agent {agent.name} failed: {e}")
                # 后续Agent依赖前序结果，出错则终止
                if agent.name == "collector":
                    break

        # 闭环验证
        verification = self.verify_loop(context)
        context["verification"] = verification
        context["pipeline_steps"] = pipeline_steps

        return context

    def verify_loop(self, context: dict) -> dict:
        """验证：建议是否覆盖风险因素、随访频率是否匹配、预警是否一致"""
        assessor = context.get("assessor", {}).get("rule_analysis", {})
        recommender = context.get("recommender", {}).get("rule_analysis", {})

        if assessor.get("error") or recommender.get("error"):
            return {"consistent": False, "gaps": ["Agent执行异常，无法验证"], "summary": "验证失败"}

        gaps = []
        # 1. 建议是否覆盖所有风险因素
        risk_factors = assessor.get("risk_factors", [])
        treatment_suggestions = recommender.get("treatment_suggestions", [])
        alert_suggestions = recommender.get("alert_suggestions", [])
        lifestyle_advice = recommender.get("lifestyle_advice", [])
        # 建议域映射
        suggestion_domain_map = {"中医治疗": "中医证候", "证型演变": "中医证候"}
        covered_domains = set()
        for s in treatment_suggestions:
            mapped = suggestion_domain_map.get(s.get("type", ""), s.get("type", ""))
            covered_domains.add(mapped)
        for a in alert_suggestions:
            covered_domains.add(a.get("source", ""))
        for l in lifestyle_advice:
            if l.get("category") == "饮食":
                covered_domains.add("中医证候")
        # 检查每个风险域是否有对应建议
        factor_domains = set(f.get("domain", "") for f in risk_factors)
        uncovered = factor_domains - covered_domains - {"趋势恶化"}  # 趋势恶化由随访频率覆盖
        if uncovered:
            gaps.append(f"以下风险域未覆盖建议：{', '.join(uncovered)}")

        # 2. 随访频率是否匹配风险等级
        risk_level = assessor.get("risk_level", "low")
        followup = recommender.get("followup_plan", {}).get("frequency", "")
        expected_freq = {"low": "每月随访", "medium": "每周随访", "high": "每日/密切监测"}
        if followup != expected_freq.get(risk_level, ""):
            gaps.append(f"随访频率({followup})与风险等级({risk_level})不匹配")

        # 3. 预警是否与风险评分一致
        alert_flags = assessor.get("alert_flags", [])
        alert_suggestions = recommender.get("alert_suggestions", [])
        if len(alert_flags) > 0 and len(alert_suggestions) == 0:
            gaps.append("存在预警标记但未生成对应预警建议")
        # 高风险必须有预警
        if risk_level == "high" and len(alert_flags) == 0:
            gaps.append("高风险但无预警标记")

        consistent = len(gaps) == 0
        summary = "闭环验证通过，建议与风险一致" if consistent else f"发现{len(gaps)}个不一致项：{'；'.join(gaps)}"

        return {"consistent": consistent, "gaps": gaps, "summary": summary}