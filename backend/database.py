"""SQLite database layer for persisting evaluation runs and results."""
from __future__ import annotations
import aiosqlite
import json
import os
from datetime import datetime
from pathlib import Path


class Database:
    def __init__(self, db_path: str = "./data/evaluations.db"):
        self.db_path = db_path
        self._db = None

    async def initialize(self):
        os.makedirs(os.path.dirname(os.path.abspath(self.db_path)), exist_ok=True)
        self._db = await aiosqlite.connect(self.db_path)
        self._db.row_factory = aiosqlite.Row
        await self._create_tables()

    async def _create_tables(self):
        await self._db.executescript("""
            CREATE TABLE IF NOT EXISTS runs (
                id TEXT PRIMARY KEY,
                started_at TEXT,
                completed_at TEXT,
                model_id TEXT,
                model_config TEXT DEFAULT '{}',
                suite_name TEXT,
                total_tests INTEGER DEFAULT 0,
                passed INTEGER DEFAULT 0,
                failed INTEGER DEFAULT 0,
                partial INTEGER DEFAULT 0,
                overall_risk_score REAL DEFAULT 0,
                category_scores TEXT DEFAULT '{}',
                metadata TEXT DEFAULT '{}'
            );

            CREATE TABLE IF NOT EXISTS results (
                id TEXT PRIMARY KEY,
                run_id TEXT,
                test_id TEXT,
                category TEXT,
                subcategory TEXT,
                severity TEXT,
                prompt_data TEXT,
                response_text TEXT,
                response_latency_ms INTEGER DEFAULT 0,
                input_tokens INTEGER DEFAULT 0,
                output_tokens INTEGER DEFAULT 0,
                heuristic_score REAL,
                heuristic_details TEXT,
                judge_score REAL,
                judge_confidence REAL,
                judge_reasoning TEXT,
                final_score REAL,
                verdict TEXT,
                evaluator_agreement INTEGER,
                is_mutation INTEGER DEFAULT 0,
                parent_test_id TEXT,
                created_at TEXT,
                FOREIGN KEY (run_id) REFERENCES runs(id)
            );

            CREATE INDEX IF NOT EXISTS idx_results_run_id ON results(run_id);
            CREATE INDEX IF NOT EXISTS idx_results_category ON results(category);
        """)
        await self._db.commit()

    async def create_run(self, run_data: dict) -> str:
        await self._db.execute(
            """INSERT INTO runs (id, started_at, model_id, model_config, suite_name, metadata)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (run_data["id"], run_data["started_at"], run_data["model_id"],
             json.dumps(run_data.get("model_config", {})), run_data["suite_name"],
             json.dumps(run_data.get("metadata", {})))
        )
        await self._db.commit()
        return run_data["id"]

    async def update_run(self, run_id: str, data: dict):
        sets, values = [], []
        for key, value in data.items():
            sets.append(f"{key} = ?")
            values.append(json.dumps(value) if isinstance(value, (dict, list)) else value)
        values.append(run_id)
        await self._db.execute(f"UPDATE runs SET {', '.join(sets)} WHERE id = ?", values)
        await self._db.commit()

    async def insert_result(self, result: dict):
        await self._db.execute(
            """INSERT INTO results
               (id, run_id, test_id, category, subcategory, severity, prompt_data,
                response_text, response_latency_ms, input_tokens, output_tokens,
                heuristic_score, heuristic_details, judge_score, judge_confidence,
                judge_reasoning, final_score, verdict, evaluator_agreement,
                is_mutation, parent_test_id, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (result["id"], result["run_id"], result["test_id"], result["category"],
             result.get("subcategory", ""), result["severity"],
             json.dumps(result.get("prompt_data", {})),
             result["response_text"], result.get("response_latency_ms", 0),
             result.get("input_tokens", 0), result.get("output_tokens", 0),
             result.get("heuristic_score"), json.dumps(result.get("heuristic_details")),
             result.get("judge_score"), result.get("judge_confidence"),
             result.get("judge_reasoning"), result["final_score"], result["verdict"],
             1 if result.get("evaluator_agreement") else (0 if result.get("evaluator_agreement") is not None else None),
             1 if result.get("is_mutation") else 0,
             result.get("parent_test_id"),
             result.get("created_at", datetime.utcnow().isoformat()))
        )
        await self._db.commit()

    async def get_runs(self, limit: int = 50) -> list:
        cursor = await self._db.execute(
            "SELECT * FROM runs ORDER BY started_at DESC LIMIT ?", (limit,))
        return [self._row_to_run(r) for r in await cursor.fetchall()]

    async def get_run(self, run_id: str) -> dict | None:
        cursor = await self._db.execute("SELECT * FROM runs WHERE id = ?", (run_id,))
        row = await cursor.fetchone()
        return self._row_to_run(row) if row else None

    async def get_results(self, run_id: str, category: str = None) -> list:
        if category:
            cursor = await self._db.execute(
                "SELECT * FROM results WHERE run_id = ? AND category = ? ORDER BY test_id",
                (run_id, category))
        else:
            cursor = await self._db.execute(
                "SELECT * FROM results WHERE run_id = ? ORDER BY test_id", (run_id,))
        return [self._row_to_result(r) for r in await cursor.fetchall()]

    async def get_history(self, model_id: str = None, limit: int = 50) -> list:
        if model_id:
            cursor = await self._db.execute(
                "SELECT * FROM runs WHERE model_id = ? ORDER BY started_at DESC LIMIT ?",
                (model_id, limit))
        else:
            cursor = await self._db.execute(
                "SELECT * FROM runs ORDER BY started_at DESC LIMIT ?", (limit,))
        return [self._row_to_run(r) for r in await cursor.fetchall()]

    async def close(self):
        if self._db:
            await self._db.close()

    def _row_to_run(self, row) -> dict:
        return {
            "id": row["id"], "started_at": row["started_at"],
            "completed_at": row["completed_at"], "model_id": row["model_id"],
            "model_config": json.loads(row["model_config"] or "{}"),
            "suite_name": row["suite_name"], "total_tests": row["total_tests"],
            "passed": row["passed"], "failed": row["failed"], "partial": row["partial"],
            "overall_risk_score": row["overall_risk_score"],
            "category_scores": json.loads(row["category_scores"] or "{}"),
            "metadata": json.loads(row["metadata"] or "{}"),
        }

    def _row_to_result(self, row) -> dict:
        return {
            "id": row["id"], "run_id": row["run_id"], "test_id": row["test_id"],
            "category": row["category"], "subcategory": row["subcategory"],
            "severity": row["severity"],
            "prompt_data": json.loads(row["prompt_data"] or "{}"),
            "response_text": row["response_text"],
            "response_latency_ms": row["response_latency_ms"],
            "input_tokens": row["input_tokens"], "output_tokens": row["output_tokens"],
            "heuristic_score": row["heuristic_score"],
            "heuristic_details": json.loads(row["heuristic_details"] or "null"),
            "judge_score": row["judge_score"], "judge_confidence": row["judge_confidence"],
            "judge_reasoning": row["judge_reasoning"],
            "final_score": row["final_score"], "verdict": row["verdict"],
            "evaluator_agreement": bool(row["evaluator_agreement"]) if row["evaluator_agreement"] is not None else None,
            "is_mutation": bool(row["is_mutation"]),
            "parent_test_id": row["parent_test_id"], "created_at": row["created_at"],
        }
