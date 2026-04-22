from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from wb_auto_replies.app.db.models import Feedback, ReplyDraft


class AntiRepeatService:
    def get_recent_drafts(self, db: Session, feedback: Feedback, limit: int = 10) -> list[str]:
        stmt = (
            select(ReplyDraft)
            .where(ReplyDraft.shop_id == feedback.shop_id)
            .order_by(ReplyDraft.created_at.desc())
            .limit(limit)
        )
        rows = db.scalars(stmt).all()
        return [row.draft_text.strip() for row in rows if row.draft_text]

    def ensure_not_repeated(self, text: str, recent_drafts: list[str]) -> tuple[str, dict[str, object]]:
        normalized = text.strip()
        exact_repeat = normalized in {item.strip() for item in recent_drafts}
        starts_same = any(
            normalized[:80] and item.strip()[:80] == normalized[:80]
            for item in recent_drafts
            if item.strip()
        )

        flags = {
            "exact_repeat": exact_repeat,
            "starts_same": starts_same,
        }

        if exact_repeat:
            normalized = f"{normalized}\n\nС уважением, команда магазина."
        elif starts_same:
            normalized = normalized.replace("Спасибо", "Благодарим", 1)

        return normalized, flags
