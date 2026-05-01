import json, os
from app.services.analysis_engine import load_analysis_config, call_local_model


class BaseAgent:
    name = ""
    description = ""

    def run(self, context: dict) -> dict:
        rule_result = self.execute_rules(context)
        model_result = None
        config = load_analysis_config()
        if config.get("model_provider") == "ollama" and config.get("ollama_url"):
            model_result = self.execute_model(context, rule_result)
        confidence = self.compute_confidence(rule_result, model_result)
        return {
            "agent": self.name,
            "description": self.description,
            "rule_analysis": rule_result,
            "model_analysis": model_result,
            "confidence": confidence,
        }

    def execute_rules(self, context: dict) -> dict:
        raise NotImplementedError

    def execute_model(self, context: dict, rule_result: dict) -> str | None:
        prompt = self.build_prompt(context, rule_result)
        if not prompt:
            return None
        return call_local_model(prompt)

    def build_prompt(self, context: dict, rule_result: dict) -> str:
        return ""

    def compute_confidence(self, rule_result: dict, model_result: str | None) -> float:
        if model_result:
            return 0.9
        return 0.75