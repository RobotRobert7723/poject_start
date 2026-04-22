from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from wb_auto_replies.app.db.models import Feedback, FeedbackMedia
from wb_auto_replies.app.media.schemas import VisionSummaryResult


class VisionAnalysisService:
    def analyze_feedback_media(self, db: Session, feedback: Feedback) -> VisionSummaryResult | None:
        media_items = db.scalars(
            select(FeedbackMedia).where(FeedbackMedia.feedback_id == feedback.id)
        ).all()
        if not media_items:
            return None

        photo_count = sum(1 for item in media_items if item.media_type == "photo")
        video_count = sum(1 for item in media_items if item.media_type == "video")

        if photo_count and video_count:
            summary = f"У отзыва есть {photo_count} фото и {video_count} видео. Нужен визуальный учет в ответе."
        elif photo_count:
            summary = f"У отзыва есть {photo_count} фото. Нужен визуальный учет в ответе."
        else:
            summary = f"У отзыва есть {video_count} видео. Нужен визуальный учет в ответе."

        result = VisionSummaryResult(summary=summary, confidence=0.3, status="stubbed")
        for item in media_items:
            item.vision_status = result.status
            item.vision_summary = result.summary
            item.vision_confidence = result.confidence
        return result
