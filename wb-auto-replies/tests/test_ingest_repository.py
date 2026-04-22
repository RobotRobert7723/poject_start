from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from wb_auto_replies.app.db.base import Base
from wb_auto_replies.app.db.models import Feedback, FeedbackRaw, Shop
from wb_auto_replies.app.ingest.repository import IngestRepository
from wb_auto_replies.app.wb.schemas import NormalizedFeedback


def make_normalized(*, text: str = "Great product", updated_suffix: str = "00") -> NormalizedFeedback:
    return NormalizedFeedback(
        source_api="active",
        feedback_id="fb-1",
        feedback_thread_key="thread-1",
        created_date=datetime(2026, 4, 22, 9, 0, tzinfo=UTC),
        updated_date=datetime.fromisoformat(f"2026-04-22T09:{updated_suffix}:00+00:00"),
        stars=5,
        text=text,
        pros="pros",
        cons="cons",
        user_name_raw="Иван",
        has_photo=True,
        has_video=False,
        media_urls=[{"media_type": "photo", "media_url": "https://example.com/1.jpg"}],
        nm_id=123,
        imt_id=456,
        product_name="Product",
        supplier_article="SKU-1",
        brand_name="Brand",
        subject_id=1,
        subject_name="Subject",
        parent_feedback_id=None,
        child_feedback_id=None,
        answer_text_current=None,
        answer_state_current=None,
        raw_payload={"id": "fb-1", "text": text, "updatedAt": f"2026-04-22T09:{updated_suffix}:00Z"},
        source_hash=f"hash-{text}-{updated_suffix}",
    )


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


def test_save_raw_payload_is_idempotent() -> None:
    db = make_session()
    shop = create_shop(db)
    repo = IngestRepository()
    normalized = make_normalized()

    first = repo.save_raw_payload(db, shop_id=shop.shop_id, normalized=normalized)
    second = repo.save_raw_payload(db, shop_id=shop.shop_id, normalized=normalized)
    db.commit()

    all_rows = db.query(FeedbackRaw).all()
    assert first.id == second.id
    assert len(all_rows) == 1


def test_upsert_feedback_is_idempotent_for_same_payload() -> None:
    db = make_session()
    shop = create_shop(db)
    repo = IngestRepository()
    normalized = make_normalized()

    first, first_created = repo.upsert_feedback(db, shop_id=shop.shop_id, normalized=normalized)
    second, second_created = repo.upsert_feedback(db, shop_id=shop.shop_id, normalized=normalized)
    db.commit()

    feedbacks = db.query(Feedback).all()
    assert first.id == second.id
    assert first_created is True
    assert second_created is False
    assert len(feedbacks) == 1
    assert feedbacks[0].version_no == 1
    assert feedbacks[0].is_latest is True


def test_upsert_feedback_creates_new_version_on_change() -> None:
    db = make_session()
    shop = create_shop(db)
    repo = IngestRepository()

    repo.upsert_feedback(db, shop_id=shop.shop_id, normalized=make_normalized(text="first", updated_suffix="00"))
    repo.upsert_feedback(db, shop_id=shop.shop_id, normalized=make_normalized(text="second", updated_suffix="05"))
    db.commit()

    feedbacks = db.query(Feedback).order_by(Feedback.version_no.asc()).all()
    assert len(feedbacks) == 2
    assert feedbacks[0].is_latest is False
    assert feedbacks[1].is_latest is True
    assert feedbacks[1].version_no == 2
    assert feedbacks[1].needs_regeneration is True
