from __future__ import annotations

from datetime import UTC, datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from wb_auto_replies.app.db.base import Base
from wb_auto_replies.app.db.models import Feedback, FeedbackMedia, ReplyDraft, ReplyPublication, Shop, SyncState
from wb_auto_replies.app.health.service import HealthService


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


def test_check_sync_health_marks_stale_sync() -> None:
    db = make_session()
    shop = create_shop(db)
    db.add(
        SyncState(
            shop_id=shop.shop_id,
            source_api="active",
            last_success_at=datetime.now(UTC) - timedelta(hours=30),
            last_attempt_at=datetime.now(UTC) - timedelta(hours=30),
            last_cursor_json=None,
            last_error_text=None,
            stats_json=None,
        )
    )
    db.commit()

    state = HealthService().check_sync_health(db, shop, "active")

    assert state.status == "warn"
    assert state.lag_seconds is not None


def test_check_stuck_drafts_warns() -> None:
    db = make_session()
    shop = create_shop(db)
    feedback = Feedback(
        shop_id=shop.shop_id,
        feedback_id="fb-1",
        version_no=1,
        is_latest=True,
        source_api="active",
        feedback_kind="real",
        has_photo=False,
        has_video=False,
        processing_status="enriched",
        needs_regeneration=False,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    db.add(
        ReplyDraft(
            shop_id=shop.shop_id,
            feedback_id=feedback.id,
            feedback_version_no=1,
            generator_type="gpt",
            mode="draft",
            prompt_snapshot={"a": 1},
            context_snapshot={"a": 1},
            draft_text="Спасибо",
            quality_flags_json={"a": 1},
            status="generated",
            created_at=datetime.now(UTC) - timedelta(hours=30),
        )
    )
    db.commit()

    state = HealthService().check_stuck_drafts(db, shop)

    assert state.status == "warn"


def test_check_publish_failures_marks_error() -> None:
    db = make_session()
    shop = create_shop(db)
    db.add(
        ReplyPublication(
            shop_id=shop.shop_id,
            feedback_id=1,
            draft_id=1,
            published_text="text",
            wb_response_json=None,
            publish_status="failed",
            published_at=None,
            error_text="boom",
        )
    )
    db.commit()

    state = HealthService().check_publish_failures(db, shop)

    assert state.status == "error"
    assert state.error_count_24h == 1


def test_check_media_backlog_warns() -> None:
    db = make_session()
    shop = create_shop(db)
    db.add(
        FeedbackMedia(
            shop_id=shop.shop_id,
            feedback_id=1,
            media_type="photo",
            media_url="https://example.com/1.jpg",
            created_at=datetime.now(UTC),
        )
    )
    db.commit()

    state = HealthService().check_media_backlog(db, shop)

    assert state.status == "warn"
