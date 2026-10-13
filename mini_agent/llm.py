"""LLM client: OpenRouter (OpenAI-compatible chat completions)."""

import json
import os

import requests

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = "nvidia/nemotron-3-super-120b-a12b:free"


class ChatError(RuntimeError):
    pass


class OpenRouterClient:
    def __init__(self, model: str | None = None, api_key: str | None = None, timeout: float = 180.0):
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ChatError("OPENROUTER_API_KEY is not set")
        self.model = model or os.environ.get("AGENT_MODEL") or DEFAULT_MODEL
        self.timeout = timeout

    def chat(self, messages: list[dict], tools: list[dict] | None = None) -> dict:
        payload: dict = {"model": self.model, "messages": messages, "temperature": 0.0}
        if tools:
            payload["tools"] = tools
        response = requests.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=self.timeout,
        )
        if response.status_code != 200:
            raise ChatError(f"HTTP {response.status_code}: {response.text[:500]}")
        data = response.json()
        try:
            return data["choices"][0]["message"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ChatError(f"unexpected response shape: {json.dumps(data)[:500]}") from exc
