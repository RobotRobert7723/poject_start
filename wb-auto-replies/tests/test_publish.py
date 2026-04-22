from __future__ import annotations

from datetime import UTC, datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from wb_auto_replies.app.db.base import Base
from wb_auto_replies.app.db.models import Feedback, ReplyDraft, Shop
from wb_auto_replies.app.publish.client import PublishClientError, WbPublishClient
from wb_auto_replies.app.publish.service import PublishEligibilityError, PublishService


def make_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)()


def create_shop(db: Session, mode: str = "draft") -> Shop:
    shop = Shop(
        shop_name="Test Shop",
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


def create_feedback(db: Session, shop_id: int, is_latest: bool = True, version_no: int = 1) -> Feedback:
    feedback = Feedback(
        shop_id=shop_id,
        feedback_id="fb-1",
        feedback_thread_key="thread-1",
        version_no=version_no,
        is_latest=is_latest,
        source_api="active",
        feedback_kind="real",
        created_date=datetime.now(UTC),
        updated_date=datetime.now(UTC),
        stars=5,
        text="Хороший товар",
        pros=None,
        cons=None,
        user_name_raw="Иван",
        safe_salutation="Здравствуйте, Иван!",
        safe_name="Иван",
        name_confidence=0.95,
        has_photo=False,
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


def create_draft(db: Session, shop_id: int, feedback_id: int, version_no: int = 1) -> ReplyDraft:
    draft = ReplyDraft(
        shop_id=shop_id,
        feedback_id=feedback_id,
        feedback_version_no=version_no,
        generator_type="gpt",
        mode="draft",
        prompt_snapshot={"test": True},
        context_snapshot={"test": True},
        draft_text="Спасибо за отзыв!",
        quality_flags_json={"test": True},
        status="generated",
        created_at=datetime.now(UTC),
    )
    db.add(draft)
    db.commit()
    db.refresh(draft)
    return draft


def test_publish_is_blocked_when_shop_not_in_publish_mode() -> None:
    db = make_session()
    shop = create_shop(db, mode="draft")
    feedback = create_feedback(db, shop.shop_id)
    draft = create_draft(db, shop.shop_id, feedback.id)

    with pytest.raises(PublishEligibilityError):
        PublishService().publish(db, shop, feedback, draft)


class FailingPublishClient(WbPublishClient):
    def publish_reply(self, feedback: Feedback, draft: ReplyDraft):  # type: ignore[override]
        raise PublishClientError("temporary publish failure")


def test_publish_records_dry_run_publication() -> None:
    db = make_session()
    shop = create_shop(db, mode="publish")
    feedback = create_feedback(db, shop.shop_id)
    draft = create_draft(db, shop.shop_id, feedback.id)

    publication = PublishService().publish(db, shop, feedback, draft)

    assert publication.publish_status == "dry_run"
    assert publication.wb_response_json is not None


def test_publish_records_failure_when_client_errors() -> None:
    db = make_session()
    shop = create_shop(db, mode="publish")
    feedback = create_feedback(db, shop.shop_id)
    draft = create_draft(db, shop.shop_id, feedback.id)

    publication = PublishService(client=FailingPublishClient()).publish(db, shop, feedback, draft)

    assert publication.publish_status == "failed"
    assert publication.error_text == "temporary publish failure"
