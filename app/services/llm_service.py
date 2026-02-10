from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

import requests

from app.config import AppConfig


@dataclass
class LLMResult:
    ok: bool
    text: str
    message: str


class LLMService:
    def __init__(self) -> None:
        self.config = AppConfig.from_env()

    def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        fallback_text: str,
        temperature: float = 0.4,
        max_tokens: int = 350,
    ) -> LLMResult:
        if self.config.llm_provider != "groq":
            return LLMResult(ok=False, text=fallback_text, message=f"Unsupported provider: {self.config.llm_provider}")
        if not self.config.groq_api_key:
            return LLMResult(ok=False, text=fallback_text, message="Missing GROQ_API_KEY.")

        payload: dict[str, Any] = {
            "model": self.config.groq_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self.config.groq_api_key}",
            "Content-Type": "application/json",
        }

        url = "https://api.groq.com/openai/v1/chat/completions"
        backoff = 1.0
        for attempt in range(4):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=35)
            except Exception as exc:  # pragma: no cover - network variance
                if attempt == 3:
                    return LLMResult(ok=False, text=fallback_text, message=str(exc))
                time.sleep(backoff)
                backoff *= 2
                continue

            if response.status_code == 200:
                data = response.json()
                text = data["choices"][0]["message"]["content"].strip()
                return LLMResult(ok=True, text=text, message="ok")

            if response.status_code == 429 and attempt < 3:
                time.sleep(backoff)
                backoff *= 2
                continue

            if attempt == 3:
                return LLMResult(
                    ok=False,
                    text=fallback_text,
                    message=f"HTTP {response.status_code}: {response.text[:250]}",
                )

            time.sleep(backoff)
            backoff *= 2

        return LLMResult(ok=False, text=fallback_text, message="Unknown failure.")

