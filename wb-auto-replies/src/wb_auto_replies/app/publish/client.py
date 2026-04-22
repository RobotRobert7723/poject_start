from __future__ import annotations

from dataclasses import dataclass

from wb_auto_replies.app.db.models import Feedback, ReplyDraft


@dataclass(slots=True)
class PublishResult:
    status: str
    response_payload: dict | None
    error_text: str | None = None


class WbPublishClient:
    def publish_reply(self, feedback: Feedback, draft: ReplyDraft) -> PublishResult:
        return PublishResult(
            status="dry_run",
            response_payload={
                "message": "Publish disabled. Dry-run only.",
                "feedback_id": feedback.feedback_id,
                "draft_id": draft.id,
            },
            error_text=None,
        )
