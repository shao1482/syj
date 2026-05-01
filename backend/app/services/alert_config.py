import json, os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "alert_config.json")

DEFAULT_CONFIG = {
    "lab_thresholds": {
        "alt": {"high": 40, "low": None, "label": "ALT"},
        "ast": {"high": 40, "low": None, "label": "AST"},
        "hgb": {"high": 160, "low": 90, "label": "HGB"},
        "wbc": {"high": 9.5, "low": 3.5, "label": "WBC"},
        "plt": {"high": 300, "low": 100, "label": "PLT"},
        "tbil": {"high": 17.1, "low": None, "label": "TBIL"},
        "rbc": {"high": 5.5, "low": 3.5, "label": "RBC"},
        "alb": {"high": None, "low": 35, "label": "ALB"},
    },
    "combined_rules": [
        {"name": "肝纤维化风险", "message": "ALT升高 + AST/ALT>1，提示肝纤维化风险", "level": "high", "enabled": True},
        {"name": "胆汁淤积倾向", "message": "ALT升高 + TBIL升高，提示胆汁淤积倾向", "level": "high", "enabled": True},
        {"name": "贫血合并感染", "message": "HGB偏低 + WBC偏高，提示贫血合并感染", "level": "high", "enabled": True},
    ],
    "tcm_change_threshold": 5,
    "qol_drop_ratio": 0.7,
    "followup_overdue_days": 30,
    "dynamic_threshold_ratio": 1.2,
}


def load_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    config = DEFAULT_CONFIG.copy()
    save_config(config)
    return config


def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def get_alert_config():
    return load_config()


def update_alert_config(new_config):
    save_config(new_config)
    return new_config


def get_lab_thresholds():
    return load_config()["lab_thresholds"]


def get_combined_rules():
    return [r for r in load_config()["combined_rules"] if r.get("enabled", True)]


def get_tcm_threshold():
    return load_config()["tcm_change_threshold"]


def get_qol_ratio():
    return load_config()["qol_drop_ratio"]