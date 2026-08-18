"""Configuration loader for the LLM Security Evaluation Lab."""
import yaml
import os
from pathlib import Path
from typing import Optional, List, Dict, Any


class Config:
    """Singleton configuration loaded from config.yaml."""
    _instance = None
    _config = None

    @classmethod
    def load(cls, path: str = None) -> "Config":
        if cls._instance is None or path is not None:
            cls._instance = cls()
            config_path = path or os.environ.get("EVAL_CONFIG", "config.yaml")
            with open(config_path, "r", encoding="utf-8") as f:
                cls._config = yaml.safe_load(f)
        return cls._instance

    @classmethod
    def reset(cls):
        cls._instance = None
        cls._config = None

    @property
    def models(self) -> dict:
        return self._config.get("models", {})

    @property
    def judge(self) -> dict:
        return self._config.get("judge", {})

    @property
    def scoring(self) -> dict:
        return self._config.get("scoring", {})

    @property
    def database_path(self) -> str:
        return self._config.get("database", {}).get("path", "./data/evaluations.db")

    @property
    def rate_limits(self) -> dict:
        return self._config.get("rate_limits", {})

    @property
    def test_suites_dir(self) -> str:
        return self._config.get("test_suites_dir", "./test_suites")

    def get_model_config(self, model_id: str) -> dict:
        """Get model config with API key resolved from environment."""
        if model_id not in self.models:
            raise ValueError(f"Model '{model_id}' not found in config. Available: {list(self.models.keys())}")
        cfg = self.models[model_id].copy()
        api_key_env = cfg.get("api_key_env", "")
        cfg["api_key"] = os.environ.get(api_key_env, "")
        return cfg

    def get_category_weight(self, category: str) -> float:
        return self.scoring.get("category_weights", {}).get(category, 0.5)

    def get_severity_weight(self, severity: str) -> float:
        return self.scoring.get("severity_weights", {}).get(severity, 1)

    def get_available_models(self) -> List[str]:
        return list(self.models.keys())
