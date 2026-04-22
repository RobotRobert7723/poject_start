from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from wb_auto_replies.app.db.models import Feedback, SemanticReplyTemplate


class DraftContextService:
    def get_article_context(self, db: Session, feedback: Feedback, limit: int = 10) -> list[str]:
        if feedback.nm_id is None:
            return []
        stmt = (
            select(Feedback)
            .where(
                Feedback.shop_id == feedback.shop_id,
                Feedback.nm_id == feedback.nm_id,
                Feedback.id != feedback.id,
                Feedback.is_latest.is_(True),
            )
            .order_by(Feedback.created_date.desc())
            .limit(limit)
        )
        rows = db.scalars(stmt).all()
        return [row.text for row in rows if row.text]

    def get_semantic_templates(self, db: Session, shop_id: int, limit: int = 10) -> list[str]:
        stmt = (
            select(SemanticReplyTemplate)
            .where(
                SemanticReplyTemplate.active.is_(True),
                (SemanticReplyTemplate.shop_id == shop_id) | (SemanticReplyTemplate.shop_id.is_(None)),
            )
            .order_by(SemanticReplyTemplate.priority.asc())
            .limit(limit)
        )
        rows = db.scalars(stmt).all()
        return [row.template_text for row in rows]
