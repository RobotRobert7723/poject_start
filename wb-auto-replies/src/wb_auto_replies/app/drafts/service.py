from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from wb_auto_replies.app.db.models import Feedback, KarmicReplyRule, ReplyDraft
from wb_auto_replies.app.drafts.anti_repeat import AntiRepeatService
from wb_auto_replies.app.drafts.context import DraftContextService
from wb_auto_replies.app.drafts.validators import DraftValidator
from wb_auto_replies.app.gpt.client import GptClient
from wb_auto_replies.app.gpt.prompts import build_real_review_system_prompt, build_real_review_user_prompt
from wb_auto_replies.app.gpt.schemas import GptGenerationRequest


class DraftGenerationService:
    def __init__(
        self,
        context_service: DraftContextService | None = None,
        validator: DraftValidator | None = None,
        gpt_client: GptClient | None = None,
        anti_repeat_service: AntiRepeatService | None = None,
    ) -> None:
        self.context_service = context_service or DraftContextService()
        self.validator = validator or DraftValidator()
        self.gpt_client = gpt_client or GptClient()
        self.anti_repeat_service = anti_repeat_service or AntiRepeatService()

    def generate_for_feedback(self, db: Session, feedback: Feedback, mode: str = "draft") -> ReplyDraft:
        if feedback.feedback_kind == "karmic":
            return self._generate_karmic_draft(db, feedback, mode)
        if feedback.feedback_kind == "real":
            return self._generate_real_draft(db, feedback, mode)
        raise ValueError(f"Unsupported feedback kind: {feedback.feedback_kind}")

    def _generate_karmic_draft(self, db: Session, feedback: Feedback, mode: str) -> ReplyDraft:
        stmt = (
            select(KarmicReplyRule)
            .where(
                KarmicReplyRule.shop_id == feedback.shop_id,
                KarmicReplyRule.active.is_(True),
                KarmicReplyRule.stars_from <= (feedback.stars or 0),
                KarmicReplyRule.stars_to >= (feedback.stars or 0),
            )
            .order_by(KarmicReplyRule.stars_from.asc())
            .limit(1)
        )
        rule = db.execute(stmt).scalar_one_or_none()
        if rule is None:
            raise ValueError("No karmic reply rule configured")

        text = self.validator.validate(rule.reply_text)
        recent_drafts = self.anti_repeat_service.get_recent_drafts(db, feedback)
        text, repeat_flags = self.anti_repeat_service.ensure_not_repeated(text, recent_drafts)
        draft = ReplyDraft(
            shop_id=feedback.shop_id,
            feedback_id=feedback.id,
            feedback_version_no=feedback.version_no,
            generator_type="template",
            mode=mode,
            prompt_snapshot={"rule_id": rule.id, "generator": "template"},
            context_snapshot={"stars": feedback.stars},
            draft_text=text,
            quality_flags_json={"path": "karmic", **repeat_flags},
            status="generated",
            created_at=datetime.now(UTC),
        )
        db.add(draft)
        return draft

    def _generate_real_draft(self, db: Session, feedback: Feedback, mode: str) -> ReplyDraft:
        article_context = self.context_service.get_article_context(db, feedback)
        semantic_templates = self.context_service.get_semantic_templates(db, feedback.shop_id)
        media_summary = None

        request = GptGenerationRequest(
            system_prompt=build_real_review_system_prompt(),
            user_prompt=build_real_review_user_prompt(
                feedback=feedback,
                safe_salutation=feedback.safe_salutation or "Здравствуйте!",
                article_context=article_context,
                semantic_templates=semantic_templates,
                media_summary=media_summary,
            ),
            model="gpt-4.1-mini",
            max_tokens=220,
            temperature=0.4,
        )
        result = self.gpt_client.generate(request)
        text = self.validator.validate(result.text)
        text = self.validator.prevent_unsafe_name(text, feedback.safe_name)
        recent_drafts = self.anti_repeat_service.get_recent_drafts(db, feedback)
        text, repeat_flags = self.anti_repeat_service.ensure_not_repeated(text, recent_drafts)

        draft = ReplyDraft(
            shop_id=feedback.shop_id,
            feedback_id=feedback.id,
            feedback_version_no=feedback.version_no,
            generator_type="gpt",
            mode=mode,
            prompt_snapshot=result.prompt_snapshot,
            context_snapshot={
                "article_context": article_context,
                "semantic_templates": semantic_templates,
                "media_summary": media_summary,
            },
            draft_text=text,
            quality_flags_json={"path": "real", **repeat_flags},
            status="generated",
            created_at=datetime.now(UTC),
        )
        db.add(draft)
        return draft
