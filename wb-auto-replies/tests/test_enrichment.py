from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from wb_auto_replies.app.classifier.service import FeedbackClassifier
from wb_auto_replies.app.db.base import Base
from wb_auto_replies.app.db.models import Feedback, FeedbackMedia, Shop
from wb_auto_replies.app.ingest.enrich import FeedbackEnrichmentService
from wb_auto_replies.app.names.service import DEFAULT_SALUTATION, NameSafetyService


def make_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)()


def create_shop(db: Session) -> Shop:
    shop = Shop(
        shop_name="Test Shop",
        wb_token="token",
        active=True,
        mode="draft",
        gpt_model=None,
        settings_json=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(shop)
    db.commit()
    db.refresh(shop)
    return shop


def create_feedback(db: Session, shop_id: int, **kwargs: object) -> Feedback:
    feedback = Feedback(
        shop_id=shop_id,
        feedback_id=str(kwargs.get("feedback_id", "fb-1")),
        feedback_thread_key="thread-1",
        version_no=1,
        is_latest=True,
        source_api=str(kwargs.get("source_api", "active")),
        feedback_kind="unknown",
        created_date=datetime.now(UTC),
        updated_date=datetime.now(UTC),
        stars=kwargs.get("stars", 5),
        text=kwargs.get("text", "Хороший товар"),
        pros=None,
        cons=None,
        user_name_raw=kwargs.get("user_name_raw", "Иван"),
        safe_salutation=None,
        safe_name=None,
        name_confidence=None,
        has_photo=False,
        has_video=False,
        nm_id=123,
        imt_id=None,
        product_name=None,
        supplier_article=None,
        brand_name=None,
        subject_id=None,
        subject_name=None,
        parent_feedback_id=kwargs.get("parent_feedback_id"),
        child_feedback_id=None,
        answer_text_current=None,
        answer_state_current=kwargs.get("answer_state_current"),
        processing_status="normalized",
        needs_regeneration=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


def test_classifier_marks_archive_feedback_as_karmic() -> None:
    classifier = FeedbackClassifier()
    feedback = Feedback(
        shop_id=1,
        feedback_id="fb-1",
        version_no=1,
        is_latest=True,
        source_api="archive",
        feedback_kind="unknown",
        has_photo=False,
        has_video=False,
        processing_status="normalized",
        needs_regeneration=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    assert classifier.classify(feedback) == "karmic"


def test_name_safety_uses_fallback_for_unsafe_name() -> None:
    result = NameSafetyService().analyze("user_123")
    assert result.safe_salutation == DEFAULT_SALUTATION
    assert result.safe_name is None
    assert result.should_use_name is False


def test_name_safety_allows_simple_name() -> None:
    result = NameSafetyService().analyze("Иван")
    assert result.safe_salutation == "Здравствуйте, Иван!"
    assert result.safe_name == "Иван"
    assert result.should_use_name is True


def test_enrichment_updates_feedback_flags_and_salutation() -> None:
    db = make_session()
    shop = create_shop(db)
    feedback = create_feedback(db, shop.shop_id, user_name_raw="Иван")
    db.add(
        FeedbackMedia(
            shop_id=shop.shop_id,
            feedback_id=feedback.id,
            media_type="photo",
            media_url="https://example.com/1.jpg",
            created_at=datetime.now(UTC),
        )
    )
    db.commit()

    enriched = FeedbackEnrichmentService().enrich_feedback(db, feedback)

    assert enriched.feedback_kind == "real"
    assert enriched.safe_salutation == "Здравствуйте, Иван!"
    assert enriched.safe_name == "Иван"
    assert enriched.name_confidence == Decimal("0.95") or enriched.name_confidence == 0.95
    assert enriched.has_photo is True
    assert enriched.has_video is False
    assert enriched.processing_status == "enriched"


def test_enrichment_marks_changed_feedback_for_regeneration() -> None:
    db = make_session()
    shop = create_shop(db)
    feedback = create_feedback(db, shop.shop_id, parent_feedback_id="fb-parent")

    enriched = FeedbackEnrichmentService().enrich_feedback(db, feedback)

    assert enriched.needs_regeneration is True
