from __future__ import annotations

from datetime import UTC, datetime
from typing import Protocol

from sqlalchemy.orm import Session

from wb_auto_replies.app.ingest.normalize import normalize_feedback
from wb_auto_replies.app.ingest.repository import IngestRepository
from wb_auto_replies.app.ingest.sync_state import SyncStateRepository
from wb_auto_replies.app.wb.schemas import NormalizedFeedback, WbApiRequest, WbApiResponse


class FetchFeedbacksClient(Protocol):
    source_api: str

    def fetch_feedbacks(self, request: WbApiRequest) -> WbApiResponse:
        ...


class IngestService:
    def __init__(
        self,
        sync_state_repository: SyncStateRepository | None = None,
        ingest_repository: IngestRepository | None = None,
    ) -> None:
        self.sync_state_repository = sync_state_repository or SyncStateRepository()
        self.ingest_repository = ingest_repository or IngestRepository()

    def fetch_and_store(
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
            for item in normalized:
                self.ingest_repository.save_raw_payload(
                    db,
                    shop_id=shop_id,
                    normalized=item,
                    fetched_at=now,
                )
                self.ingest_repository.upsert_feedback(
                    db,
                    shop_id=shop_id,
                    normalized=item,
                    now=now,
                )
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
