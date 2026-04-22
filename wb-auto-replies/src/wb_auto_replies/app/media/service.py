from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from wb_auto_replies.app.db.models import FeedbackMedia


class MediaMetadataService:
    def summarize_flags(self, db: Session, feedback_id: int) -> tuple[bool, bool]:
        media_items = db.scalars(
            select(FeedbackMedia).where(FeedbackMedia.feedback_id == feedback_id)
        ).all()
        has_photo = any(item.media_type == "photo" for item in media_items)
        has_video = any(item.media_type == "video" for item in media_items)
        return has_photo, has_video
