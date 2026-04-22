from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from wb_auto_replies.app.db.models import Feedback, FeedbackMedia, FeedbackRaw
from wb_auto_replies.app.wb.schemas import NormalizedFeedback


class IngestRepository:
    def save_raw_payload(
        self,
        db: Session,
        *,
        shop_id: int,
        normalized: NormalizedFeedback,
        fetched_at: datetime | None = None,
    ) -> FeedbackRaw:
        stmt = select(FeedbackRaw).where(
            FeedbackRaw.shop_id == shop_id,
            FeedbackRaw.source_api == normalized.source_api,
            FeedbackRaw.feedback_id == normalized.feedback_id,
            FeedbackRaw.source_hash == normalized.source_hash,
        )
        existing = db.execute(stmt).scalar_one_or_none()
        if existing is not None:
            return existing

        raw = FeedbackRaw(
            shop_id=shop_id,
            source_api=normalized.source_api,
            feedback_id=normalized.feedback_id,
            payload_json=normalized.raw_payload,
            fetched_at=fetched_at or datetime.now(UTC),
            source_hash=normalized.source_hash,
        )
        db.add(raw)
        db.flush()
        return raw

    def upsert_feedback(
        self,
        db: Session,
        *,
        shop_id: int,
        normalized: NormalizedFeedback,
        now: datetime | None = None,
    ) -> tuple[Feedback, bool]:
        timestamp = now or datetime.now(UTC)
        latest_stmt = (
            select(Feedback)
            .where(
                Feedback.shop_id == shop_id,
                Feedback.feedback_id == normalized.feedback_id,
                Feedback.is_latest.is_(True),
            )
            .order_by(Feedback.version_no.desc())
        )
        existing_latest = db.execute(latest_stmt).scalar_one_or_none()

        if existing_latest is None:
            created = Feedback(
                shop_id=shop_id,
                feedback_id=normalized.feedback_id,
                feedback_thread_key=normalized.feedback_thread_key,
                version_no=1,
                is_latest=True,
                source_api=normalized.source_api,
                created_date=normalized.created_date,
                updated_date=normalized.updated_date,
                stars=normalized.stars,
                text=normalized.text,
                pros=normalized.pros,
                cons=normalized.cons,
                user_name_raw=normalized.user_name_raw,
                has_photo=normalized.has_photo,
                has_video=normalized.has_video,
                nm_id=normalized.nm_id,
                imt_id=normalized.imt_id,
                product_name=normalized.product_name,
                supplier_article=normalized.supplier_article,
                brand_name=normalized.brand_name,
                subject_id=normalized.subject_id,
                subject_name=normalized.subject_name,
                parent_feedback_id=normalized.parent_feedback_id,
                child_feedback_id=normalized.child_feedback_id,
                answer_text_current=normalized.answer_text_current,
                answer_state_current=normalized.answer_state_current,
                processing_status="normalized",
                needs_regeneration=False,
                created_at=timestamp,
                updated_at=timestamp,
            )
            db.add(created)
            db.flush()
            self.replace_media(db, feedback=created, normalized=normalized, created_at=timestamp)
            return created, True

        if self._same_content(existing_latest, normalized):
            existing_latest.updated_at = timestamp
            self.replace_media(db, feedback=existing_latest, normalized=normalized, created_at=timestamp)
            return existing_latest, False

        existing_latest.is_latest = False
        existing_latest.child_feedback_id = normalized.feedback_id
        existing_latest.updated_at = timestamp

        versioned = Feedback(
            shop_id=shop_id,
            feedback_id=normalized.feedback_id,
            feedback_thread_key=normalized.feedback_thread_key or existing_latest.feedback_thread_key,
            version_no=existing_latest.version_no + 1,
            is_latest=True,
            source_api=normalized.source_api,
            created_date=normalized.created_date,
            updated_date=normalized.updated_date,
            stars=normalized.stars,
            text=normalized.text,
            pros=normalized.pros,
            cons=normalized.cons,
            user_name_raw=normalized.user_name_raw,
            has_photo=normalized.has_photo,
            has_video=normalized.has_video,
            nm_id=normalized.nm_id,
            imt_id=normalized.imt_id,
            product_name=normalized.product_name,
            supplier_article=normalized.supplier_article,
            brand_name=normalized.brand_name,
            subject_id=normalized.subject_id,
            subject_name=normalized.subject_name,
            parent_feedback_id=existing_latest.feedback_id,
            child_feedback_id=normalized.child_feedback_id,
            answer_text_current=normalized.answer_text_current,
            answer_state_current=normalized.answer_state_current,
            processing_status="normalized",
            needs_regeneration=True,
            created_at=timestamp,
            updated_at=timestamp,
        )
        db.add(versioned)
        db.flush()
        self.replace_media(db, feedback=versioned, normalized=normalized, created_at=timestamp)
        return versioned, True

    def replace_media(
        self,
        db: Session,
        *,
        feedback: Feedback,
        normalized: NormalizedFeedback,
        created_at: datetime,
    ) -> None:
        existing_media = db.scalars(
            select(FeedbackMedia).where(FeedbackMedia.feedback_id == feedback.id)
        ).all()
        for item in existing_media:
            db.delete(item)
        db.flush()

        for media in normalized.media_urls:
            db.add(
                FeedbackMedia(
                    shop_id=feedback.shop_id,
                    feedback_id=feedback.id,
                    media_type=media["media_type"],
                    media_url=media["media_url"],
                    created_at=created_at,
                )
            )

    def _same_content(self, feedback: Feedback, normalized: NormalizedFeedback) -> bool:
        return all(
            [
                feedback.source_api == normalized.source_api,
                feedback.feedback_thread_key == normalized.feedback_thread_key,
                feedback.created_date == normalized.created_date,
                feedback.updated_date == normalized.updated_date,
                feedback.stars == normalized.stars,
                feedback.text == normalized.text,
                feedback.pros == normalized.pros,
                feedback.cons == normalized.cons,
                feedback.user_name_raw == normalized.user_name_raw,
                feedback.has_photo == normalized.has_photo,
                feedback.has_video == normalized.has_video,
                feedback.nm_id == normalized.nm_id,
                feedback.imt_id == normalized.imt_id,
                feedback.product_name == normalized.product_name,
                feedback.supplier_article == normalized.supplier_article,
                feedback.brand_name == normalized.brand_name,
                feedback.subject_id == normalized.subject_id,
                feedback.subject_name == normalized.subject_name,
                feedback.parent_feedback_id == normalized.parent_feedback_id,
                feedback.child_feedback_id == normalized.child_feedback_id,
                feedback.answer_text_current == normalized.answer_text_current,
                feedback.answer_state_current == normalized.answer_state_current,
            ]
        )
