from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from wb_auto_replies.app.config.seeds import SeedService
from wb_auto_replies.app.db.base import Base
from wb_auto_replies.app.db.models import KarmicReplyRule, SemanticReplyTemplate, Shop


def make_session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)()


def test_seed_service_creates_shop_and_defaults() -> None:
    db = make_session()
    service = SeedService()

    shop = service.upsert_shop(
        db,
        shop_name="Test Shop",
        wb_token="token",
        mode="draft",
        gpt_model="gpt-4.1-mini",
    )
    service.seed_karmic_rules(db, shop)
    service.seed_semantic_templates(db, shop)
    db.commit()

    shops = db.execute(select(Shop)).scalars().all()
    karmic = db.execute(select(KarmicReplyRule)).scalars().all()
    semantic = db.execute(select(SemanticReplyTemplate)).scalars().all()

    assert len(shops) == 1
    assert len(karmic) == 3
    assert len(semantic) == 3
