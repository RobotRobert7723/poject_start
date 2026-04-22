from __future__ import annotations

import re
from dataclasses import dataclass


DEFAULT_SALUTATION = "Здравствуйте!"
CYRILLIC_NAME_RE = re.compile(r"^[А-ЯЁ][а-яё]{1,29}$")
LATIN_NAME_RE = re.compile(r"^[A-Z][a-z]{1,29}$")
BAD_TOKENS = {
    "buyer",
    "client",
    "user",
    "guest",
    "admin",
    "manager",
    "test",
    "unknown",
    "аноним",
    "покупатель",
    "клиент",
    "пользователь",
    "гость",
    "тест",
}


@dataclass(slots=True)
class NameSafetyResult:
    safe_salutation: str
    safe_name: str | None
    confidence: float
    should_use_name: bool
    reason: str


class NameSafetyService:
    def analyze(self, raw_name: str | None) -> NameSafetyResult:
        if raw_name is None:
            return self._fallback("empty")

        candidate = raw_name.strip()
        if not candidate:
            return self._fallback("blank")

        lowered = candidate.casefold()
        if lowered in BAD_TOKENS:
            return self._fallback("blocked_token")

        if any(char.isdigit() for char in candidate):
            return self._fallback("contains_digit")

        if any(char in "_-.@#/\\" for char in candidate):
            return self._fallback("contains_symbol")

        parts = [part for part in candidate.split() if part]
        if len(parts) != 1:
            return self._fallback("not_single_name")

        token = parts[0]
        if CYRILLIC_NAME_RE.fullmatch(token) or LATIN_NAME_RE.fullmatch(token):
            return NameSafetyResult(
                safe_salutation=f"Здравствуйте, {token}!",
                safe_name=token,
                confidence=0.95,
                should_use_name=True,
                reason="looks_like_real_name",
            )

        return self._fallback("low_confidence")

    def _fallback(self, reason: str) -> NameSafetyResult:
        return NameSafetyResult(
            safe_salutation=DEFAULT_SALUTATION,
            safe_name=None,
            confidence=0.0,
            should_use_name=False,
            reason=reason,
        )
