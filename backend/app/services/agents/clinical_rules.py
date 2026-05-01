# 临床知识规则库（集中管理，供所有Agent引用）
from app.services.alert_config import load_config

TCM_SYNDROME_MAP = {
    "脾胃虚弱": {"desc": "面色萎黄、纳差便溏、神疲乏力", "formula": "四君子汤/参苓白术散加减", "diet": "宜食健脾益气之品，忌生冷寒凉"},
    "肝胃不和": {"desc": "胃脘胀痛、嗳气反酸、情志不畅", "formula": "柴胡疏肝散加减", "diet": "忌辛辣刺激，注意情志调摄"},
    "脾胃湿热": {"desc": "口苦口黏、脘腹痞满、舌苔黄腻", "formula": "半夏泻心汤/黄连温胆汤加减", "diet": "忌辛辣油腻甜食"},
    "胃阴不足": {"desc": "胃脘隐痛、口干便干、舌红少苔", "formula": "益胃汤/沙参麦冬汤加减", "diet": "忌燥热伤阴，宜滋阴养胃"},
}

RISK_SCORING_WEIGHTS = {"tcm": 30, "lab": 10, "qol": 10}
RISK_LEVELS = {"low": {"max": 15, "label": "低风险", "followup": "每月随访"},
               "medium": {"max": 30, "label": "中风险", "followup": "每周随访"},
               "high": {"label": "高风险", "followup": "每日/密切监测"}}

RECHECK_PLAN = {
    "low": ["血常规+肝功能每月1次", "中医证候每月评估"],
    "medium": ["血常规+肝功能每周1次", "中医证候每2周评估", "生活质量每月评估"],
    "high": ["血常规+肝功能即时复查", "中医证候每周评估", "生活质量每周评估", "胃功能指标复查"],
}


def get_lab_thresholds():
    return load_config()["lab_thresholds"]


def get_combined_rules():
    return [r for r in load_config()["combined_rules"] if r.get("enabled", True)]