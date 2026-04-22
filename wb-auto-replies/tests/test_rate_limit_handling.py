from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from wb_auto_replies.app.db.base import Base
from wb_auto_replies.app.db.models import HealthEvent, Shop, SyncState
from wb_auto_replies.app.ingest.service import IngestService
from wb_auto_replies.app.wb.client import WbRateLimitError
from wb_auto_replies.app.wb.schemas import WbApiRequest


class RateLimitedClient:
    source_api = "archive"

    def fetch_feedbacks(self, request: WbApiRequest):  # type: ignore[no-untyped-def]
        raise WbRateLimitError("rate limit hit")


def make_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)()


def create_shop(db: Session) -> Shop:
    shop = Shop(
        shop_name="Test Shop",
        wb_token="token",
        active=True,
        mode="backfill",
        gpt_model="gpt-4.1-mini",
        settings_json=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(shop)
    db.commit()
    db.refresh(shop)
    return shop


def test_rate_limit_is_recorded_without_raising() -> None:
    db = make_session()
    shop = create_shop(db)
    service = IngestService()

    result = service.fetch_and_store(
        db,
        shop_id=shop.shop_id,
        request=WbApiRequest(token="token", take=1),
        client=RateLimitedClient(),
    )

    sync_state = db.execute(select(SyncState)).scalar_one()
    event = db.execute(select(HealthEvent)).scalar_one()

    assert result == []
    assert sync_state.last_error_text == "rate limit hit"
    assert event.event_type == "rate_limited"
