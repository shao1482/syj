import json
import statistics
from app.services.agents.base_agent import BaseAgent
from app.services.agents.clinical_rules import get_lab_thresholds, TCM_SYNDROME_MAP


class AnalyzerAgent(BaseAgent):
    name = "analyzer"
    description = "指标解析Agent：标准化解析、趋势建模、异常检测、关联分析"

    def execute_rules(self, context: dict) -> dict:
        collector = context.get("collector", {}).get("rule_analysis", {})
        if not collector.get("data_available"):
            return {"error": "无数据"}

        tcm_series = collector.get("tcm_series", [])
        lab_series = collector.get("lab_series", [])
        qol_series = collector.get("qol_series", [])

        trends = self._analyze_trends(tcm_series, lab_series, qol_series)
        statistics_data = self._compute_statistics(lab_series, qol_series, tcm_series)
        anomalies = self._detect_anomalies(lab_series, tcm_series)
        correlations = self._analyze_correlations(tcm_series, lab_series)

        return {"trends": trends, "statistics": statistics_data,
                "anomalies": anomalies, "correlations": correlations}

    def _analyze_trends(self, tcm, lab, qol):
        trends = {}
        if len(tcm) >= 2:
            values = [s["total_score"] for s in tcm]
            slopes = self._compute_slope(values)
            trends["tcm_total"] = {"direction": self._detect_direction(values),
                                    "slope": slopes, "latest": values[-1],
                                    "change_from_first": values[-1] - values[0]}
        if len(lab) >= 2:
            for field in ["alt", "hgb", "wbc", "tbil"]:
                vals = [s[field] for s in lab if s.get(field) is not None]
                if len(vals) >= 2:
                    trends[f"lab_{field}"] = {"direction": self._detect_direction(vals),
                                               "slope": self._compute_slope(vals), "latest": vals[-1]}
        if len(qol) >= 2:
            values = [s["total"] for s in qol]
            trends["qol_total"] = {"direction": self._detect_direction(values),
                                    "slope": self._compute_slope(values), "latest": values[-1]}
        return trends

    def _compute_statistics(self, lab, qol, tcm):
        stats = {}
        for field in ["alt", "hgb", "wbc", "tbil", "ast", "alb"]:
            vals = [s[field] for s in lab if s.get(field) is not None]
            if len(vals) >= 2:
                stats[f"lab_{field}"] = {"mean": statistics.mean(vals), "std": statistics.stdev(vals),
                                          "min": min(vals), "max": max(vals), "latest": vals[-1],
                                          "z_score_latest": (vals[-1] - statistics.mean(vals)) / statistics.stdev(vals) if statistics.stdev(vals) > 0 else 0}
        tcm_vals = [s["total_score"] for s in tcm]
        if len(tcm_vals) >= 2:
            stats["tcm_total"] = {"mean": statistics.mean(tcm_vals), "std": statistics.stdev(tcm_vals), "latest": tcm_vals[-1]}
        qol_vals = [s["total"] for s in qol]
        if len(qol_vals) >= 2:
            stats["qol_total"] = {"mean": statistics.mean(qol_vals), "latest": qol_vals[-1]}
        return stats

    def _detect_anomalies(self, lab, tcm):
        anomalies = []
        thresholds = get_lab_thresholds()
        if lab:
            latest = lab[-1]
            for field, rule in thresholds.items():
                val = latest.get(field)
                if val is None: continue
                label = rule["label"]
                if rule.get("high") and val > rule["high"]:
                    anomalies.append({"field": field, "label": label, "value": val,
                                      "threshold": rule["high"], "type": "high", "severity": "high" if val > rule["high"] * 1.5 else "medium"})
                elif rule.get("low") and rule["low"] is not None and val < rule["low"]:
                    anomalies.append({"field": field, "label": label, "value": val,
                                      "threshold": rule["low"], "type": "low", "severity": "high" if val < rule["low"] * 0.7 else "medium"})
        if tcm:
            latest_tcm = tcm[-1]
            scores = {"脾胃虚弱": latest_tcm["spleen_stomach_weak"], "肝胃不和": latest_tcm["liver_stomachdisharmony"],
                      "脾胃湿热": latest_tcm["spleen_stomach_dampheat"], "胃阴不足": latest_tcm["stomach_yin_deficiency"]}
            dominant = max(scores, key=scores.get)
            anomalies.append({"field": "tcm_dominant", "label": dominant, "value": scores[dominant], "type": "tcm_dominant", "severity": "medium" if scores[dominant] > 10 else "low"})
        return anomalies

    def _analyze_correlations(self, tcm, lab):
        correlations = []
        if len(tcm) >= 3 and len(lab) >= 3:
            # 按日期交集取配对
            tcm_dates = {s["date"]: s["total_score"] for s in tcm}
            lab_dates = {s["date"]: s.get("alt") for s in lab if s.get("alt") is not None}
            common_dates = sorted(set(tcm_dates.keys()) & set(lab_dates.keys()))
            if len(common_dates) >= 3:
                tcm_vals = [tcm_dates[d] for d in common_dates]
                lab_vals = [lab_dates[d] for d in common_dates]
                corr = self._pearson(tcm_vals, lab_vals)
                correlations.append({"pair": "证候总分-ALT", "correlation": round(corr, 3),
                                      "interpretation": "正相关-证候加重伴随ALT升高" if corr > 0.3 else ("负相关-证候改善伴随ALT升高" if corr < -0.3 else "无明显线性关联")})
            hgb_dates = {s["date"]: s.get("hgb") for s in lab if s.get("hgb") is not None}
            common2 = sorted(set(tcm_dates.keys()) & set(hgb_dates.keys()))
            if len(common2) >= 3:
                corr2 = self._pearson([tcm_dates[d] for d in common2], [hgb_dates[d] for d in common2])
                correlations.append({"pair": "证候总分-HGB", "correlation": round(corr2, 3),
                                      "interpretation": "正相关-证候加重伴随HGB升高" if corr2 > 0.3 else ("负相关-证候加重伴随HGB降低" if corr2 < -0.3 else "无明显线性关联")})
        return correlations

    def _detect_direction(self, values):
        if len(values) < 2: return "数据不足"
        slope = self._compute_slope(values)
        if slope > 0.5: return "上升"
        elif slope < -0.5: return "下降"
        else: return "稳定"

    def _compute_slope(self, values):
        if len(values) < 2: return 0
        n = len(values)
        x = list(range(n))
        mean_x = statistics.mean(x)
        mean_y = statistics.mean(values)
        numerator = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, values))
        denominator = sum((xi - mean_x) ** 2 for xi in x)
        return numerator / denominator if denominator != 0 else 0

    def _pearson(self, x, y):
        n = len(x)
        if n < 2: return 0
        mean_x = statistics.mean(x)
        mean_y = statistics.mean(y)
        cov = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
        std_x = statistics.stdev(x) if n >= 2 else 1
        std_y = statistics.stdev(y) if n >= 2 else 1
        return cov / (n * std_x * std_y) if std_x > 0 and std_y > 0 else 0

    def build_prompt(self, context, rule_result) -> str:
        collector = context.get("collector", {}).get("rule_analysis", {})
        p = collector.get("patient_info", {})
        trends = rule_result.get("trends", {})
        anomalies = rule_result.get("anomalies", [])
        return f"请根据以下脾胃消化患者的临床数据进行深入解读：患者{p.get('name','')},{p.get('age','')}岁。趋势分析：{json.dumps(trends, ensure_ascii=False)}。异常指标：{json.dumps(anomalies, ensure_ascii=False)}。"