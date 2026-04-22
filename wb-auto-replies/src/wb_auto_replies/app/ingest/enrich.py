from __future__ import annotations

from sqlalchemy.orm import Session

from wb_auto_replies.app.classifier.service import FeedbackClassifier
from wb_auto_replies.app.db.models import Feedback
from wb_auto_replies.app.media.service import MediaMetadataService
from wb_auto_replies.app.names.service import NameSafetyService


class FeedbackEnrichmentService:
    def __init__(
        self,
        classifier: FeedbackClassifier | None = None,
        name_safety: NameSafetyService | None = None,
        media_metadata: MediaMetadataService | None = None,
    ) -> None:
        self.classifier = classifier or FeedbackClassifier()
        self.name_safety = name_safety or NameSafetyService()
        self.media_metadata = media_metadata or MediaMetadataService()

    def enrich_feedback(self, db: Session, feedback: Feedback) -> Feedback:
        feedback.feedback_kind = self.classifier.classify(feedback)

        name_result = self.name_safety.analyze(feedback.user_name_raw)
        feedback.safe_salutation = name_result.safe_salutation
        feedback.safe_name = name_result.safe_name
        feedback.name_confidence = name_result.confidence

        has_photo, has_video = self.media_metadata.summarize_flags(db, feedback.id)
        feedback.has_photo = has_photo
        feedback.has_video = has_video

        if feedback.processing_status == "normalized":
            feedback.processing_status = "enriched"

        if feedback.parent_feedback_id is not None:
            feedback.needs_regeneration = True

        return feedback
