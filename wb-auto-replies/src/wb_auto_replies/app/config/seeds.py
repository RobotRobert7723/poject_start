from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from wb_auto_replies.app.db.models import KarmicReplyRule, SemanticReplyTemplate, Shop


class SeedService:
    def upsert_shop(
        self,
        db: Session,
        *,
        shop_name: str,
        wb_token: str,
        mode: str = "draft",
        gpt_model: str = "gpt-4.1-mini",
        settings_json: dict | None = None,
    ) -> Shop:
        stmt = select(Shop).where(Shop.shop_name == shop_name)
        shop = db.execute(stmt).scalar_one_or_none()
        now = datetime.now(UTC)
        if shop is None:
            shop = Shop(
                shop_name=shop_name,
                wb_token=wb_token,
                active=True,
                mode=mode,
                gpt_model=gpt_model,
                settings_json=settings_json or {
                    "backfill": {
                        "enabled": True,
                        "batch_size": 100,
                        "max_total": 1000,
                        "start_skip": 0,
                    },
                    "draft": {
                        "enabled": True,
                        "batch_size": 100,
                        "start_skip": 0,
                    },
                },
                created_at=now,
                updated_at=now,
            )
            db.add(shop)
        else:
            shop.wb_token = wb_token
            shop.mode = mode
            shop.gpt_model = gpt_model
            if settings_json is not None:
                shop.settings_json = settings_json
            shop.updated_at = now
        db.flush()
        return shop

    def seed_karmic_rules(self, db: Session, shop: Shop) -> None:
        defaults = [
            (1, 2, "Здравствуйте! Спасибо за отзыв. Нам жаль, что товар вас не устроил. Мы учтем замечания."),
            (3, 3, "Здравствуйте! Спасибо за отзыв. Благодарим за обратную связь и учтем ваши замечания."),
            (4, 5, "Здравствуйте! Спасибо за высокую оценку и отзыв. Нам очень приятно, что товар вам понравился."),
        ]
        now = datetime.now(UTC)
        for stars_from, stars_to, reply_text in defaults:
            stmt = select(KarmicReplyRule).where(
                KarmicReplyRule.shop_id == shop.shop_id,
                KarmicReplyRule.stars_from == stars_from,
                KarmicReplyRule.stars_to == stars_to,
            )
            rule = db.execute(stmt).scalar_one_or_none()
            if rule is None:
                db.add(
                    KarmicReplyRule(
                        shop_id=shop.shop_id,
                        stars_from=stars_from,
                        stars_to=stars_to,
                        reply_text=reply_text,
                        active=True,
                        created_at=now,
                        updated_at=now,
                    )
                )

    def seed_semantic_templates(self, db: Session, shop: Shop) -> None:
        defaults = [
            ("positive", "Позитивный отзыв", "Спасибо за теплые слова и доверие к нашему товару."),
            ("quality_issue", "Проблема качества", "Спасибо за отзыв. Нам жаль, что вы столкнулись с такой ситуацией."),
            ("delivery_issue", "Проблема доставки", "Спасибо за отзыв. Сожалеем, что впечатление было испорчено доставкой или комплектацией."),
        ]
        now = datetime.now(UTC)
        for idx, (category_key, title, template_text) in enumerate(defaults, start=1):
            stmt = select(SemanticReplyTemplate).where(
                SemanticReplyTemplate.shop_id == shop.shop_id,
                SemanticReplyTemplate.category_key == category_key,
            )
            template = db.execute(stmt).scalar_one_or_none()
            if template is None:
                db.add(
                    SemanticReplyTemplate(
                        shop_id=shop.shop_id,
                        category_key=category_key,
                        title=title,
                        description=None,
                        template_text=template_text,
                        active=True,
                        priority=idx,
                        created_at=now,
                        updated_at=now,
                    )
                )
