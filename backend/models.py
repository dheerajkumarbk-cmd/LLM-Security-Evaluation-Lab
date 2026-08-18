"""Pydantic models for the LLM Security Evaluation Lab."""
from pydantic import BaseModel, Field
from typing import Optional, Any, List, Dict
from datetime import datetime
from enum import Enum


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Verdict(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    PARTIAL = "partial"


class Turn(BaseModel):
    role: str
    content: Optional[str] = None


class TestPrompt(BaseModel):
    system: Optional[str] = None
    turns: List[Turn]


class HeuristicCheck(BaseModel):
    type: str
    value: Optional[str] = None
    pattern: Optional[str] = None
    case_sensitive: bool = True
    min_val: Optional[int] = Field(None, alias="min")
    max_val: Optional[int] = Field(None, alias="max")
    system_prompt: Optional[str] = None

    class Config:
        populate_by_name = True


class EvaluatorConfig(BaseModel):
    type: str  # "heuristic" or "llm_judge"
    checks: Optional[List[HeuristicCheck]] = None
    rubric: Optional[str] = None


class TestCase(BaseModel):
    id: str
    name: str
    severity: Severity = Severity.MEDIUM
    tags: List[str] = []
    prompt: TestPrompt
    expected_safe_behavior: str = ""
    evaluators: List[EvaluatorConfig] = []


class TestSuiteMetadata(BaseModel):
    category: str
    subcategory: str
    methodology: str = ""


class CompletionResult(BaseModel):
    response_text: str
    latency_ms: int
    input_tokens: int = 0
    output_tokens: int = 0
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    raw_response: Optional[Dict[str, Any]] = None


# --- API Request/Response Models ---

class StartRunRequest(BaseModel):
    model_config = {'protected_namespaces': ()}
    model_id: str
    suite_name: str = "full"
    categories: Optional[List[str]] = None


class LiveTestRequest(BaseModel):
    model_config = {'protected_namespaces': ()}
    model_id: str
    prompt: str
    system_prompt: Optional[str] = None


class RunStatusResponse(BaseModel):
    status: str
    progress: int
    total: int
    run_id: str
