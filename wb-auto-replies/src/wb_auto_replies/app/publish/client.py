from __future__ import annotations

from dataclasses import dataclass

from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from wb_auto_replies.app.db.models import Feedback, ReplyDraft


@dataclass(slots=True)
class PublishResult:
    status: str
    response_payload: dict | None
    error_text: str | None = None


class PublishClientError(Exception):
    pass


class WbPublishClient:
    @retry(
        retry=retry_if_exception_type(PublishClientError),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        stop=stop_after_attempt(3),
        reraise=True,
    )
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
