from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from wb_auto_replies.app.db.base import Base
from wb_auto_replies.app.db.models import Feedback, FeedbackMedia, Shop
from wb_auto_replies.app.drafts.context import DraftContextService
from wb_auto_replies.app.media.vision import VisionAnalysisService


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
        gpt_model="gpt-4.1-mini",
        settings_json=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(shop)
    db.commit()
    db.refresh(shop)
    return shop


def create_feedback(db: Session, shop_id: int) -> Feedback:
    feedback = Feedback(
        shop_id=shop_id,
        feedback_id="fb-1",
        feedback_thread_key="thread-1",
        version_no=1,
        is_latest=True,
        source_api="active",
        feedback_kind="real",
        created_date=datetime.now(UTC),
        updated_date=datetime.now(UTC),
        stars=5,
        text="Товар с фото",
        pros=None,
        cons=None,
        user_name_raw="Иван",
        safe_salutation="Здравствуйте, Иван!",
        safe_name="Иван",
        name_confidence=0.95,
        has_photo=True,
        has_video=False,
        nm_id=123,
        imt_id=None,
        product_name=None,
        supplier_article=None,
        brand_name=None,
        subject_id=None,
        subject_name=None,
        parent_feedback_id=None,
        child_feedback_id=None,
        answer_text_current=None,
        answer_state_current=None,
        processing_status="enriched",
        needs_regeneration=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return feedback


def test_vision_service_persists_summary_to_media() -> None:
    db = make_session()
    shop = create_shop(db)
    feedback = create_feedback(db, shop.shop_id)
    media = FeedbackMedia(
        shop_id=shop.shop_id,
        feedback_id=feedback.id,
        media_type="photo",
        media_url="https://example.com/1.jpg",
        created_at=datetime.now(UTC),
    )
    db.add(media)
    db.commit()

    result = VisionAnalysisService().analyze_feedback_media(db, feedback)
    db.commit()
    db.refresh(media)

    assert result is not None
    assert media.vision_status == "stubbed"
    assert media.vision_summary is not None
    assert "фото" in media.vision_summary


def test_draft_context_returns_media_summary() -> None:
    db = make_session()
    shop = create_shop(db)
    feedback = create_feedback(db, shop.shop_id)
    media = FeedbackMedia(
        shop_id=shop.shop_id,
        feedback_id=feedback.id,
        media_type="photo",
        media_url="https://example.com/1.jpg",
        vision_status="done",
        vision_summary="На фото видна упаковка товара.",
        vision_confidence=0.8,
        created_at=datetime.now(UTC),
    )
    db.add(media)
    db.commit()

    summary = DraftContextService().get_media_summary(db, feedback)

    assert summary == "На фото видна упаковка товара."
