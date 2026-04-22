from __future__ import annotations

from sqlalchemy import select

from wb_auto_replies.app.config.settings import get_settings
from wb_auto_replies.app.db.models import Feedback, ReplyDraft, Shop
from wb_auto_replies.app.db.session import SessionLocal
from wb_auto_replies.app.drafts.service import DraftGenerationService
from wb_auto_replies.app.ingest.enrich import FeedbackEnrichmentService
from wb_auto_replies.app.ingest.service import IngestService
from wb_auto_replies.app.publish.service import PublishEligibilityError, PublishService
from wb_auto_replies.app.wb.active_client import ActiveFeedbacksClient
from wb_auto_replies.app.wb.archive_client import ArchiveFeedbacksClient
from wb_auto_replies.app.wb.schemas import WbApiRequest


class JobService:
    def __init__(self) -> None:
        self.settings = get_settings()
        self.ingest_service = IngestService()
        self.enrichment_service = FeedbackEnrichmentService()
        self.draft_service = DraftGenerationService()
        self.publish_service = PublishService()

    def run_backfill(self, *, shop_id: int, take: int, skip: int) -> None:
        with SessionLocal() as db:
            shop = self._get_shop(db, shop_id)
            request = WbApiRequest(token=shop.wb_token, take=take, skip=skip)
            self.ingest_service.fetch_and_store(db, shop_id=shop.shop_id, request=request, client=ArchiveFeedbacksClient())
            db.commit()

    def run_draft(self, *, shop_id: int, take: int, skip: int) -> None:
        with SessionLocal() as db:
            shop = self._get_shop(db, shop_id)
            request = WbApiRequest(token=shop.wb_token, take=take, skip=skip)
            self.ingest_service.fetch_and_store(db, shop_id=shop.shop_id, request=request, client=ActiveFeedbacksClient())
            feedbacks = db.execute(
                select(Feedback).where(Feedback.shop_id == shop.shop_id, Feedback.is_latest.is_(True))
            ).scalars().all()
            for feedback in feedbacks:
                self.enrichment_service.enrich_feedback(db, feedback)
                if feedback.feedback_kind in {"karmic", "real"}:
                    draft = self.draft_service.generate_for_feedback(db, feedback, mode="draft")
                    db.add(draft)
            db.commit()

    def run_publish(self, *, shop_id: int) -> None:
        with SessionLocal() as db:
            shop = self._get_shop(db, shop_id)
            drafts = db.execute(
                select(ReplyDraft, Feedback)
                .join(Feedback, Feedback.id == ReplyDraft.feedback_id)
                .where(ReplyDraft.shop_id == shop.shop_id, ReplyDraft.status == "generated")
            ).all()
            for draft, feedback in drafts:
                try:
                    self.publish_service.publish(db, shop, feedback, draft)
                except PublishEligibilityError:
                    continue
            db.commit()

    def _get_shop(self, db, shop_id: int) -> Shop:
        shop = db.get(Shop, shop_id)
        if shop is None:
            raise ValueError(f"Shop not found: {shop_id}")
        return shop
