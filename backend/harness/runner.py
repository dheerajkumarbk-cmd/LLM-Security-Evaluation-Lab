"""Test Harness execution engine."""
from __future__ import annotations
import asyncio
import os
import glob
import yaml
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Callable

from backend.config import Config
from backend.database import Database
from backend.models import TestCase, TestSuiteMetadata, TestPrompt, Turn, Severity
from backend.adapters.openai_adapter import OpenAIAdapter
from backend.adapters.anthropic_adapter import AnthropicAdapter
from backend.evaluators.heuristic import HeuristicEvaluator
from backend.evaluators.llm_judge import LLMJudgeEvaluator
from backend.evaluators.composite import CompositeScorer


class TestRunner:
    """Orchestrates loading test suites, querying models, evaluating responses, and saving runs."""

    def __init__(self, config: Optional[Config] = None, db: Optional[Database] = None):
        self.config = config or Config.load()
        self.db = db or Database(self.config.database_path)
        self.heuristic_evaluator = HeuristicEvaluator()
        self.composite_scorer = CompositeScorer(self.config)

    def get_adapter(self, model_id: str):
        cfg = self.config.get_model_config(model_id)
        provider = cfg.get("provider", "openai")
        model = cfg.get("model", model_id)
        api_key = cfg.get("api_key", "")
        parameters = cfg.get("parameters", {})

        if provider == "openai":
            return OpenAIAdapter(model=model, api_key=api_key, parameters=parameters)
        elif provider == "anthropic":
            return AnthropicAdapter(model=model, api_key=api_key, parameters=parameters)
        else:
            # Default to OpenAI adapter
            return OpenAIAdapter(model=model, api_key=api_key, parameters=parameters)

    def load_test_cases(self, categories: Optional[list[str]] = None) -> list[tuple[TestCase, str, str]]:
        """
        Load test cases from YAML files under test_suites_dir.
        Returns list of (TestCase, category, subcategory).
        """
        suites_dir = self.config.test_suites_dir
        results = []

        if not os.path.exists(suites_dir):
            return results

        category_dirs = [d for d in os.listdir(suites_dir) if os.path.isdir(os.path.join(suites_dir, d))]

        for cat in category_dirs:
            if categories and cat not in categories:
                continue

            cat_path = os.path.join(suites_dir, cat)
            yaml_files = glob.glob(os.path.join(cat_path, "*.yaml"))

            for yfile in yaml_files:
                if os.path.basename(yfile).startswith("_"):
                    continue
                try:
                    with open(yfile, "r", encoding="utf-8") as f:
                        data = yaml.safe_load(f)

                    metadata = data.get("metadata", {})
                    subcat = metadata.get("subcategory", cat)
                    tests_data = data.get("tests", [])

                    for tdata in tests_data:
                        tc = TestCase(**tdata)
                        results.append((tc, cat, subcat))
                except Exception as e:
                    print(f"Error loading test file {yfile}: {e}")

        return results

    async def run_evaluation(self, model_id: str, categories: Optional[list[str]] = None, suite_name: str = "full", progress_cb: Optional[Callable] = None) -> str:
        """Run full evaluation workflow asynchronously."""
        await self.db.initialize()
        run_id = str(uuid.uuid4())
        started_at = datetime.utcnow().isoformat()

        adapter = self.get_adapter(model_id)

        # Initialize judge adapter
        judge_cfg = self.config.judge
        judge_api_key = os.environ.get(judge_cfg.get("api_key_env", "OPENAI_API_KEY"), "")
        judge_adapter = OpenAIAdapter(model=judge_cfg.get("model", "gpt-4o-mini"), api_key=judge_api_key)
        judge_evaluator = LLMJudgeEvaluator(judge_adapter)

        # Create initial run record
        await self.db.create_run({
            "id": run_id,
            "started_at": started_at,
            "model_id": model_id,
            "model_config": self.config.models.get(model_id, {}),
            "suite_name": suite_name,
            "metadata": {"categories_requested": categories}
        })

        test_tuples = self.load_test_cases(categories)
        total = len(test_tuples)
        completed_results = []

        for idx, (test_case, cat, subcat) in enumerate(test_tuples):
            if progress_cb:
                await progress_cb(idx, total, test_case.id)

            # Query target model
            completion = await adapter.complete(test_case.prompt)

            # Evaluate heuristics
            heuristic_result = None
            heuristic_config = next((e for e in test_case.evaluators if e.type == "heuristic"), None)
            if heuristic_config and heuristic_config.checks:
                heuristic_result = self.heuristic_evaluator.evaluate(test_case, completion, heuristic_config.checks)

            # Evaluate LLM Judge
            judge_result = None
            judge_config = next((e for e in test_case.evaluators if e.type == "llm_judge"), None)
            if judge_config and judge_config.rubric:
                judge_result = await judge_evaluator.evaluate(test_case, completion, judge_config.rubric)

            # Score result
            scored = self.composite_scorer.score_single_result(test_case, heuristic_result, judge_result)

            result_entry = {
                "id": str(uuid.uuid4()),
                "run_id": run_id,
                "test_id": test_case.id,
                "category": cat,
                "subcategory": subcat,
                "severity": test_case.severity.value,
                "prompt_data": test_case.prompt.model_dump(),
                "response_text": completion.response_text,
                "response_latency_ms": completion.latency_ms,
                "input_tokens": completion.input_tokens,
                "output_tokens": completion.output_tokens,
                "heuristic_score": scored["heuristic_score"],
                "heuristic_details": scored["heuristic_details"],
                "judge_score": scored["judge_score"],
                "judge_confidence": scored["judge_confidence"],
                "judge_reasoning": scored["judge_reasoning"],
                "final_score": scored["final_score"],
                "verdict": scored["verdict"],
                "evaluator_agreement": scored["evaluator_agreement"],
            }

            await self.db.insert_result(result_entry)
            completed_results.append(result_entry)

        # Calculate final run summary & risk scores
        summary = self.composite_scorer.calculate_run_summary(completed_results)
        completed_at = datetime.utcnow().isoformat()

        await self.db.update_run(run_id, {
            "completed_at": completed_at,
            "total_tests": summary["total_tests"],
            "passed": summary["passed"],
            "failed": summary["failed"],
            "partial": summary["partial"],
            "overall_risk_score": summary["overall_risk_score"],
            "category_scores": summary["category_scores"],
        })

        if progress_cb:
            await progress_cb(total, total, "Complete")

        return run_id
