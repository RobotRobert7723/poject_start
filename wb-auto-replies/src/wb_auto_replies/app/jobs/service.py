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

    def run_backfill(self, *, shop_id: int) -> None:
        with SessionLocal() as db:
            shop = self._get_shop(db, shop_id)
            settings = (shop.settings_json or {}).get("backfill", {})
            if not settings.get("enabled", True):
                return
            batch_size = int(settings.get("batch_size", 100))
            max_total = int(settings.get("max_total", batch_size))
            start_skip = int(settings.get("start_skip", 0))

            loaded = 0
            skip = start_skip
            while loaded < max_total:
                request = WbApiRequest(token=shop.wb_token, take=batch_size, skip=skip)
                normalized = self.ingest_service.fetch_and_store(db, shop_id=shop.shop_id, request=request, client=ArchiveFeedbacksClient())
                db.commit()
                batch_count = len(normalized)
                if batch_count == 0:
                    break
                loaded += batch_count
                skip += batch_size
                if batch_count < batch_size:
                    break

    def run_draft(self, *, shop_id: int) -> None:
        with SessionLocal() as db:
            shop = self._get_shop(db, shop_id)
            settings = (shop.settings_json or {}).get("draft", {})
            if not settings.get("enabled", True):
                return
            batch_size = int(settings.get("batch_size", 100))
            start_skip = int(settings.get("start_skip", 0))
            request = WbApiRequest(token=shop.wb_token, take=batch_size, skip=start_skip)
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
