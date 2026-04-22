from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from wb_auto_replies.app.db.models import Feedback, FeedbackMedia, SemanticReplyTemplate


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

    def get_media_summary(self, db: Session, feedback: Feedback) -> str | None:
        stmt = (
            select(FeedbackMedia)
            .where(FeedbackMedia.feedback_id == feedback.id)
            .order_by(FeedbackMedia.id.asc())
        )
        media_items = db.scalars(stmt).all()
        summaries = [item.vision_summary for item in media_items if item.vision_summary]
        if summaries:
            return summaries[0]
        return None

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
