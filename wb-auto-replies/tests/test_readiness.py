from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from wb_auto_replies.app.db.base import Base
from wb_auto_replies.app.db.models import KarmicReplyRule, ReplyPublication, SemanticReplyTemplate, Shop
from wb_auto_replies.app.drafts.service import DraftGenerationService
from wb_auto_replies.app.gpt.schemas import GptGenerationResult
from wb_auto_replies.app.ingest.enrich import FeedbackEnrichmentService
from wb_auto_replies.app.ingest.repository import IngestRepository
from wb_auto_replies.app.publish.service import PublishEligibilityError, PublishService
from wb_auto_replies.app.wb.schemas import NormalizedFeedback


class StubGptClient:
    def generate(self, request):  # type: ignore[no-untyped-def]
        return GptGenerationResult(
            text="Спасибо за отзыв! Мы рады, что товар вам понравился.",
            model=request.model,
            prompt_snapshot={"stub": True},
            raw_response={"stub": True},
        )


def make_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)()


def create_shop(db: Session, name: str, mode: str) -> Shop:
    shop = Shop(
        shop_name=name,
        wb_token="token",
        active=True,
        mode=mode,
        gpt_model="gpt-4.1-mini",
        settings_json=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(shop)
    db.commit()
    db.refresh(shop)
    return shop


def normalized_feedback(*, feedback_id: str, source_api: str, text: str, stars: int, nm_id: int) -> NormalizedFeedback:
    return NormalizedFeedback(
        source_api=source_api,
        feedback_id=feedback_id,
        feedback_thread_key=feedback_id,
        created_date=datetime.now(UTC),
        updated_date=datetime.now(UTC),
        stars=stars,
        text=text,
        pros=None,
        cons=None,
        user_name_raw="Иван",
        has_photo=False,
        has_video=False,
        media_urls=[],
        nm_id=nm_id,
        imt_id=None,
        product_name="Product",
        supplier_article="SKU",
        brand_name="Brand",
        subject_id=1,
        subject_name="Subject",
        parent_feedback_id=None,
        child_feedback_id=None,
        answer_text_current=None,
        answer_state_current=None,
        raw_payload={"id": feedback_id, "text": text},
        source_hash=f"hash-{feedback_id}",
    )


def test_backfill_mode_ingests_without_publication() -> None:
    db = make_session()
    shop = create_shop(db, "Shop Backfill", "backfill")
    repo = IngestRepository()
    feedback, created = repo.upsert_feedback(
        db,
        shop_id=shop.shop_id,
        normalized=normalized_feedback(
            feedback_id="fb-archive-1",
            source_api="archive",
            text="",
            stars=5,
            nm_id=1,
        ),
    )
    db.commit()

    assert created is True
    assert feedback.source_api == "archive"
    assert db.execute(select(ReplyPublication)).scalars().all() == []


def test_draft_mode_generates_draft_but_does_not_publish() -> None:
    db = make_session()
    shop = create_shop(db, "Shop Draft", "draft")
    db.add(
        SemanticReplyTemplate(
            shop_id=shop.shop_id,
            category_key="positive",
            title="Positive",
            description=None,
            template_text="Спасибо за добрые слова.",
            active=True,
            priority=1,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
    )
    db.commit()

    repo = IngestRepository()
    feedback, _ = repo.upsert_feedback(
        db,
        shop_id=shop.shop_id,
        normalized=normalized_feedback(
            feedback_id="fb-active-1",
            source_api="active",
            text="Очень хороший товар",
            stars=5,
            nm_id=10,
        ),
    )
    db.commit()

    FeedbackEnrichmentService().enrich_feedback(db, feedback)
    draft = DraftGenerationService(gpt_client=StubGptClient()).generate_for_feedback(db, feedback, mode="draft")
    db.add(draft)
    db.commit()

    assert draft.mode == "draft"
    assert db.execute(select(ReplyPublication)).scalars().all() == []


def test_controlled_publish_safe_path_records_dry_run_only() -> None:
    db = make_session()
    shop = create_shop(db, "Shop Publish", "publish")
    db.add(
        SemanticReplyTemplate(
            shop_id=shop.shop_id,
            category_key="positive",
            title="Positive",
            description=None,
            template_text="Спасибо за добрые слова.",
            active=True,
            priority=1,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
    )
    db.commit()

    repo = IngestRepository()
    feedback, _ = repo.upsert_feedback(
        db,
        shop_id=shop.shop_id,
        normalized=normalized_feedback(
            feedback_id="fb-active-2",
            source_api="active",
            text="Очень хороший товар",
            stars=5,
            nm_id=11,
        ),
    )
    db.commit()

    FeedbackEnrichmentService().enrich_feedback(db, feedback)
    draft = DraftGenerationService(gpt_client=StubGptClient()).generate_for_feedback(db, feedback, mode="publish")
    db.add(draft)
    db.commit()

    publication = PublishService().publish(db, shop, feedback, draft)
    db.commit()

    assert publication.publish_status == "dry_run"
    assert publication.published_at is None


def test_multi_store_isolation_keeps_context_separate() -> None:
    db = make_session()
    shop_a = create_shop(db, "Shop A", "draft")
    shop_b = create_shop(db, "Shop B", "draft")
    db.add_all([
        SemanticReplyTemplate(
            shop_id=shop_a.shop_id,
            category_key="positive",
            title="Positive A",
            description=None,
            template_text="Шаблон магазина A.",
            active=True,
            priority=1,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
        SemanticReplyTemplate(
            shop_id=shop_b.shop_id,
            category_key="positive",
            title="Positive B",
            description=None,
            template_text="Шаблон магазина B.",
            active=True,
            priority=1,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        ),
    ])
    db.commit()

    repo = IngestRepository()
    feedback_a, _ = repo.upsert_feedback(
        db,
        shop_id=shop_a.shop_id,
        normalized=normalized_feedback(
            feedback_id="fb-a",
            source_api="active",
            text="Отзыв A",
            stars=5,
            nm_id=21,
        ),
    )
    feedback_b, _ = repo.upsert_feedback(
        db,
        shop_id=shop_b.shop_id,
        normalized=normalized_feedback(
            feedback_id="fb-b",
            source_api="active",
            text="Отзыв B",
            stars=5,
            nm_id=21,
        ),
    )
    db.commit()

    FeedbackEnrichmentService().enrich_feedback(db, feedback_a)
    FeedbackEnrichmentService().enrich_feedback(db, feedback_b)

    draft_a = DraftGenerationService(gpt_client=StubGptClient()).generate_for_feedback(db, feedback_a, mode="draft")
    draft_b = DraftGenerationService(gpt_client=StubGptClient()).generate_for_feedback(db, feedback_b, mode="draft")

    assert draft_a.context_snapshot is not None
    assert draft_b.context_snapshot is not None
    assert draft_a.context_snapshot["semantic_templates"] == ["Шаблон магазина A."]
    assert draft_b.context_snapshot["semantic_templates"] == ["Шаблон магазина B."]
