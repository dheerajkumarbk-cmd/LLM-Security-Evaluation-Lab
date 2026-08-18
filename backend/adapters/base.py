"""Abstract base class for target model adapters."""
from abc import ABC, abstractmethod
from typing import Optional
from backend.models import Turn, CompletionResult, TestPrompt


class ModelAdapter(ABC):
    """Abstract interface for LLM model adapters."""

    @abstractmethod
    async def complete(self, prompt: TestPrompt, parameters: Optional[dict] = None) -> CompletionResult:
        """Send a prompt (system + turns) to the target model and return a standardized result."""
        pass

    @abstractmethod
    def model_id(self) -> str:
        """Return the unique model identifier string."""
        pass
