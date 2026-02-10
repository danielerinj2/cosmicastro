from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.config import AppConfig
from app.services.llm_service import LLMService


def main() -> int:
    config = AppConfig.from_env()
    missing = config.missing_groq_env()
    if missing:
        print(f"Missing env vars: {', '.join(missing)}")
        return 1

    service = LLMService()
    result = service.generate(
        system_prompt="You are concise.",
        user_prompt="Reply with exactly GROQ_OK",
        fallback_text="GROQ_FALLBACK",
        temperature=0,
        max_tokens=6,
    )
    print(f"[groq] {'OK' if result.ok else 'FAIL'} - {result.message}")
    print(f"[groq] model={config.groq_model}")
    print(f"[groq] response={result.text.strip()}")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

