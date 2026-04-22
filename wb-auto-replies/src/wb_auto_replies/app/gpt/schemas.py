from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class GptGenerationRequest:
    system_prompt: str
    user_prompt: str
    model: str
    max_tokens: int = 300
    temperature: float = 0.4


@dataclass(slots=True)
class GptGenerationResult:
    text: str
    model: str
    prompt_snapshot: dict[str, Any]
    raw_response: dict[str, Any] | None = None
