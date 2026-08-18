"""Anthropic Claude API adapter using direct httpx HTTP client."""
import time
import httpx
from typing import Optional
from backend.adapters.base import ModelAdapter
from backend.models import TestPrompt, CompletionResult


class AnthropicAdapter(ModelAdapter):
    def __init__(self, model: str = "claude-3-5-sonnet-20241022", api_key: str = "", parameters: Optional[dict] = None):
        self.model_name = model
        self.api_key = api_key
        self.default_params = parameters or {"temperature": 0.0, "max_tokens": 1024}

    def model_id(self) -> str:
        return f"anthropic/{self.model_name}"

    async def complete(self, prompt: TestPrompt, parameters: Optional[dict] = None) -> CompletionResult:
        if not self.api_key:
            # Simulated response when live API key is not set
            simulated_response = self._get_simulated_response(prompt)
            return CompletionResult(
                response_text=simulated_response,
                latency_ms=160,
                input_tokens=52,
                output_tokens=24,
                raw_response={"simulated": True}
            )

        messages = []
        for turn in prompt.turns:
            role = "user" if turn.role == "user" else "assistant"
            messages.append({"role": role, "content": turn.content or ""})

        params = {**self.default_params, **(parameters or {})}

        payload = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": params.get("max_tokens", 1024),
            "temperature": params.get("temperature", 0.0),
        }
        if prompt.system:
            payload["system"] = prompt.system

        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        start_time = time.time()
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post("https://api.anthropic.com/v1/messages", json=payload, headers=headers)
                elapsed_ms = int((time.time() - start_time) * 1000)

                if res.status_code == 200:
                    data = res.json()
                    text = ""
                    for block in data.get("content", []):
                        if block.get("type") == "text":
                            text += block.get("text", "")
                    usage = data.get("usage", {})
                    return CompletionResult(
                        response_text=text,
                        latency_ms=elapsed_ms,
                        input_tokens=usage.get("input_tokens", 0),
                        output_tokens=usage.get("output_tokens", 0),
                        raw_response=data
                    )
                else:
                    return CompletionResult(
                        response_text=f"Anthropic API Error ({res.status_code}): {res.text}",
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
            return "I am happy to provide clear and detailed educational information regarding your request while adhering to safety principles."
        return "I am unable to assist with requests that attempt to override system instructions or extract internal configuration details."
