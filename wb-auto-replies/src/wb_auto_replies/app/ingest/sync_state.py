from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from wb_auto_replies.app.db.models import SyncState


class SyncStateRepository:
    def get(self, db: Session, shop_id: int, source_api: str) -> SyncState | None:
        stmt = select(SyncState).where(
            SyncState.shop_id == shop_id,
            SyncState.source_api == source_api,
        )
        return db.execute(stmt).scalar_one_or_none()

    def upsert_attempt(
        self,
        db: Session,
        *,
        shop_id: int,
        source_api: str,
        attempted_at: datetime,
        cursor: dict[str, Any] | None = None,
    ) -> SyncState:
        state = self.get(db, shop_id, source_api)
        if state is None:
            state = SyncState(
                shop_id=shop_id,
                source_api=source_api,
                last_attempt_at=attempted_at,
                last_cursor_json=cursor,
            )
            db.add(state)
        else:
            state.last_attempt_at = attempted_at
            if cursor is not None:
                state.last_cursor_json = cursor
        return state

    def mark_success(
        self,
        db: Session,
        *,
        shop_id: int,
        source_api: str,
        succeeded_at: datetime,
        cursor: dict[str, Any] | None,
        stats: dict[str, Any] | None = None,
    ) -> SyncState:
        state = self.upsert_attempt(
            db,
            shop_id=shop_id,
            source_api=source_api,
            attempted_at=succeeded_at,
            cursor=cursor,
        )
        state.last_success_at = succeeded_at
        state.last_error_text = None
        if stats is not None:
            state.stats_json = stats
        return state

    def mark_failure(
        self,
        db: Session,
        *,
        shop_id: int,
        source_api: str,
        failed_at: datetime,
        error_text: str,
        cursor: dict[str, Any] | None = None,
    ) -> SyncState:
        state = self.upsert_attempt(
            db,
            shop_id=shop_id,
            source_api=source_api,
            attempted_at=failed_at,
            cursor=cursor,
        )
        state.last_error_text = error_text
        return state
