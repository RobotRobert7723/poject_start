from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from wb_auto_replies.app.db.models import Feedback, ReplyDraft, ReplyPublication, Shop
from wb_auto_replies.app.publish.client import PublishResult, WbPublishClient


class PublishEligibilityError(Exception):
    pass


class PublishService:
    def __init__(self, client: WbPublishClient | None = None) -> None:
        self.client = client or WbPublishClient()

    def validate_publish(self, shop: Shop, feedback: Feedback, draft: ReplyDraft) -> None:
        if shop.mode != "publish":
            raise PublishEligibilityError("Shop is not in publish mode")
        if not feedback.is_latest:
            raise PublishEligibilityError("Only latest feedback version can be published")
        if draft.feedback_version_no != feedback.version_no:
            raise PublishEligibilityError("Draft version does not match latest feedback version")
        if draft.status != "generated":
            raise PublishEligibilityError("Draft is not ready for publish")

        existing_stmt = select(ReplyPublication).where(
            ReplyPublication.feedback_id == feedback.id,
            ReplyPublication.publish_status == "published",
        )
        existing = db.execute(existing_stmt).scalar_one_or_none()
        if existing is not None:
            raise PublishEligibilityError("Feedback already has published reply")

    def publish(self, db: Session, shop: Shop, feedback: Feedback, draft: ReplyDraft) -> ReplyPublication:
        self.validate_publish(shop, feedback, draft)
        result = self.client.publish_reply(feedback, draft)
        publication = ReplyPublication(
            shop_id=shop.shop_id,
            feedback_id=feedback.id,
            draft_id=draft.id,
            published_text=draft.draft_text,
            wb_response_json=result.response_payload,
            publish_status=result.status,
            published_at=datetime.now(UTC) if result.status == "published" else None,
            error_text=result.error_text,
        )
        db.add(publication)
        if result.status == "published":
            feedback.answer_text_current = draft.draft_text
            feedback.answer_state_current = "wbRu"
        return publication

