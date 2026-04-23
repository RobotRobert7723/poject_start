from __future__ import annotations

import re
from dataclasses import dataclass


DEFAULT_SALUTATION = "Здравствуйте!"
CYRILLIC_NAME_RE = re.compile(r"^[А-ЯЁ][а-яё]{2,19}$")
LATIN_NAME_RE = re.compile(r"^[A-Z][a-z]{2,19}$")
COMMON_RU_NAMES = {
    'иван','мария','анна','дмитрий','алексей','елена','ольга','наталья','ирина','алёна','алена','екатерина','анастасия','светлана','татьяна','марина','николай','роман','андрей','андрей','андрей','александра','алина','инна','валентина','зоя','зара','ина'
}
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
        lowered_token = token.casefold()

        if token.endswith(('ов','ев','ёв','ин','ын','ский','цкий','ская','цкая','дзе','ян','янц','оглы','улы')):
            return self._fallback("looks_like_surname")

        if CYRILLIC_NAME_RE.fullmatch(token):
            if lowered_token not in COMMON_RU_NAMES:
                return self._fallback("unknown_cyrillic_name")
            return NameSafetyResult(
                safe_salutation=f"Здравствуйте, {token}!",
                safe_name=token,
                confidence=0.95,
                should_use_name=True,
                reason="known_ru_name",
            )

        if LATIN_NAME_RE.fullmatch(token):
            return self._fallback("latin_not_allowed")

        return self._fallback("low_confidence")

    def _fallback(self, reason: str) -> NameSafetyResult:
        return NameSafetyResult(
            safe_salutation=DEFAULT_SALUTATION,
            safe_name=None,
            confidence=0.0,
            should_use_name=False,
            reason=reason,
        )
