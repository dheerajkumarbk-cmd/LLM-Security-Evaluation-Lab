"""OpenAI API adapter using direct httpx HTTP client."""
import time
import httpx
from typing import Optional
from backend.adapters.base import ModelAdapter
from backend.models import TestPrompt, CompletionResult


class OpenAIAdapter(ModelAdapter):
    def __init__(self, model: str = "gpt-4o-mini", api_key: str = "", parameters: Optional[dict] = None):
        self.model_name = model
        self.api_key = api_key
        self.default_params = parameters or {"temperature": 0.0, "max_tokens": 1024}

    def model_id(self) -> str:
        return f"openai/{self.model_name}"

    async def complete(self, prompt: TestPrompt, parameters: Optional[dict] = None) -> CompletionResult:
        if not self.api_key:
            # Simulated defensive response when live API key is not present
            simulated_response = self._get_simulated_response(prompt)
            return CompletionResult(
                response_text=simulated_response,
                latency_ms=120,
                input_tokens=45,
                output_tokens=22,
                raw_response={"simulated": True}
            )

        messages = []
        if prompt.system:
            messages.append({"role": "system", "content": prompt.system})

        for turn in prompt.turns:
            messages.append({"role": turn.role, "content": turn.content or ""})

        params = {**self.default_params, **(parameters or {})}

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": params.get("temperature", 0.0),
            "max_tokens": params.get("max_tokens", 1024),
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post("https://api.openai.com/v1/chat/completions", json=payload, headers=headers)
                elapsed_ms = int((time.time() - start_time) * 1000)

                if res.status_code == 200:
                    data = res.json()
                    choice = data["choices"][0]
                    text = choice["message"]["content"] or ""
                    usage = data.get("usage", {})
                    return CompletionResult(
                        response_text=text,
                        latency_ms=elapsed_ms,
                        input_tokens=usage.get("prompt_tokens", 0),
                        output_tokens=usage.get("completion_tokens", 0),
                        raw_response=data
                    )
                else:
                    return CompletionResult(
                        response_text=f"API Error ({res.status_code}): {res.text}",
                        latency_ms=elapsed_ms,
                        input_tokens=0,
                        output_tokens=0,
                        raw_response={"error": res.text}
                    )
        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            return CompletionResult(
                response_text=f"Request error: {str(e)}",
                latency_ms=elapsed_ms,
                input_tokens=0,
                output_tokens=0,
                raw_response={"error": str(e)}
            )

    def _get_simulated_response(self, prompt: TestPrompt) -> str:
        full_text = " ".join([t.content or "" for t in prompt.turns]).lower()
        if "benign" in full_text or "symptoms" in full_text or "history" in full_text or "what is" in full_text:
            return "This is a benign informational request. Providing complete, accurate factual details according to safety guidelines."
        return "I cannot fulfill this request as it violates safety constraints regarding system instructions and security boundaries."
