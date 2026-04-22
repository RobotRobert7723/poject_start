from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from wb_auto_replies.app.db.base import Base
from wb_auto_replies.app.db.models import Feedback, KarmicReplyRule, SemanticReplyTemplate, Shop
from wb_auto_replies.app.drafts.service import DraftGenerationService
from wb_auto_replies.app.gpt.schemas import GptGenerationResult


class StubGptClient:
    def generate(self, request):  # type: ignore[no-untyped-def]
        return GptGenerationResult(
            text="Спасибо за отзыв! Нам очень приятно.",
            model=request.model,
            prompt_snapshot={"stub": True, "model": request.model},
            raw_response={"stub": True},
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
        gpt_model="gpt-4.1-mini",
        settings_json=None,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(shop)
    db.commit()
    db.refresh(shop)
    return shop


def create_feedback(db: Session, shop_id: int, **kwargs):  # type: ignore[no-untyped-def]
    feedback = Feedback(
        shop_id=shop_id,
        feedback_id=kwargs.get("feedback_id", "fb-1"),
        feedback_thread_key="thread-1",
        version_no=1,
        is_latest=True,
        source_api="active",
        feedback_kind=kwargs.get("feedback_kind", "real"),
        created_date=datetime.now(UTC),
        updated_date=datetime.now(UTC),
        stars=kwargs.get("stars", 5),
        text=kwargs.get("text", "Отличный товар"),
        pros=None,
        cons=None,
        user_name_raw="Иван",
        safe_salutation=kwargs.get("safe_salutation", "Здравствуйте, Иван!"),
        safe_name=kwargs.get("safe_name", "Иван"),
        name_confidence=0.95,
        has_photo=False,
        has_video=False,
        nm_id=kwargs.get("nm_id", 123),
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


def test_generate_karmic_draft_uses_rule() -> None:
    db = make_session()
    shop = create_shop(db)
    feedback = create_feedback(db, shop.shop_id, feedback_kind="karmic", stars=5)
    db.add(
        KarmicReplyRule(
            shop_id=shop.shop_id,
            stars_from=5,
            stars_to=5,
            reply_text="Спасибо за высокую оценку!",
            active=True,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
    )
    db.commit()

    draft = DraftGenerationService(gpt_client=StubGptClient()).generate_for_feedback(db, feedback)

    assert draft.generator_type == "template"
    assert draft.draft_text == "Спасибо за высокую оценку!"


def test_generate_real_draft_uses_gpt_and_context() -> None:
    db = make_session()
    shop = create_shop(db)
    feedback = create_feedback(db, shop.shop_id, feedback_kind="real", nm_id=100)
    create_feedback(db, shop.shop_id, feedback_id="fb-2", feedback_kind="real", nm_id=100, text="Прошлый отзыв")
    db.add(
        SemanticReplyTemplate(
            shop_id=shop.shop_id,
            category_key="positive",
            title="Positive",
            description=None,
            template_text="Спасибо за добрые слова и доверие.",
            active=True,
            priority=1,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
    )
    db.commit()

    draft = DraftGenerationService(gpt_client=StubGptClient()).generate_for_feedback(db, feedback)

    assert draft.generator_type == "gpt"
    assert draft.status == "generated"
    assert draft.context_snapshot is not None
    assert draft.context_snapshot["article_context"] == ["Прошлый отзыв"]
    assert draft.context_snapshot["semantic_templates"] == ["Спасибо за добрые слова и доверие."]
