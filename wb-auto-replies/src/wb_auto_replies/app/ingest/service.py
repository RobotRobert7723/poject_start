from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol

from sqlalchemy.orm import Session

from wb_auto_replies.app.ingest.normalize import normalize_feedback
from wb_auto_replies.app.ingest.sync_state import SyncStateRepository
from wb_auto_replies.app.wb.schemas import NormalizedFeedback, WbApiRequest, WbApiResponse


class FetchFeedbacksClient(Protocol):
    source_api: str

    def fetch_feedbacks(self, request: WbApiRequest) -> WbApiResponse:
        ...


class IngestService:
    def __init__(self, sync_state_repository: SyncStateRepository | None = None) -> None:
        self.sync_state_repository = sync_state_repository or SyncStateRepository()

    def fetch_and_normalize(
        self,
        db: Session,
        *,
        shop_id: int,
        request: WbApiRequest,
        client: FetchFeedbacksClient,
    ) -> list[NormalizedFeedback]:
        now = datetime.now(UTC)
        try:
            response = client.fetch_feedbacks(request)
            normalized = [normalize_feedback(client.source_api, item) for item in response.items]
            self.sync_state_repository.mark_success(
                db,
                shop_id=shop_id,
                source_api=client.source_api,
                succeeded_at=now,
                cursor=response.cursor,
                stats={"count": len(response.items), "total": response.total},
            )
            return normalized
        except Exception as exc:
            self.sync_state_repository.mark_failure(
                db,
                shop_id=shop_id,
                source_api=client.source_api,
                failed_at=now,
                error_text=str(exc),
            )
            raise
