from __future__ import annotations

from wb_auto_replies.app.names.service import DEFAULT_SALUTATION


class DraftValidationError(Exception):
    pass


class DraftValidator:
    def validate(self, text: str) -> str:
        normalized = text.strip()
        if not normalized:
            raise DraftValidationError("Draft is empty")
        if len(normalized) > 1500:
            raise DraftValidationError("Draft is too long")
        return normalized

    def prevent_unsafe_name(self, text: str, safe_name: str | None) -> str:
        if safe_name is None and DEFAULT_SALUTATION not in text:
            return f"{DEFAULT_SALUTATION} {text}".strip()
        return text
