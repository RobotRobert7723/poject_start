from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from wb_auto_replies.app.db.models import Feedback, FeedbackMedia, HealthEvent, HealthState, ReplyDraft, ReplyPublication, Shop, SyncState


class HealthService:
    def write_event(
        self,
        db: Session,
        *,
        component: str,
        severity: str,
        event_type: str,
        message: str,
        shop_id: int | None = None,
        payload: dict[str, Any] | None = None,
    ) -> HealthEvent:
        event = HealthEvent(
            shop_id=shop_id,
            component=component,
            severity=severity,
            event_type=event_type,
            message=message,
            payload_json=payload,
            created_at=datetime.now(UTC),
        )
        db.add(event)
        return event

    def upsert_state(
        self,
        db: Session,
        *,
        component: str,
        status: str,
        shop_id: int | None = None,
        last_success_at: datetime | None = None,
        last_error_at: datetime | None = None,
        error_count_24h: int = 0,
        lag_seconds: int | None = None,
    ) -> HealthState:
        stmt = select(HealthState).where(
            HealthState.shop_id == shop_id,
            HealthState.component == component,
        )
        state = db.execute(stmt).scalar_one_or_none()
        now = datetime.now(UTC)
        if state is None:
            state = HealthState(
                shop_id=shop_id,
                component=component,
                status=status,
                last_success_at=last_success_at,
                last_error_at=last_error_at,
                error_count_24h=error_count_24h,
                lag_seconds=lag_seconds,
                updated_at=now,
            )
            db.add(state)
        else:
            state.status = status
            state.last_success_at = last_success_at
            state.last_error_at = last_error_at
            state.error_count_24h = error_count_24h
            state.lag_seconds = lag_seconds
            state.updated_at = now
        return state

    def check_sync_health(self, db: Session, shop: Shop, source_api: str, stale_after_hours: int = 24) -> HealthState:
        stmt = select(SyncState).where(SyncState.shop_id == shop.shop_id, SyncState.source_api == source_api)
        sync = db.execute(stmt).scalar_one_or_none()
        now = datetime.now(UTC)
        if sync is None or sync.last_success_at is None:
            self.write_event(
                db,
                shop_id=shop.shop_id,
                component=f"sync:{source_api}",
                severity="warn",
                event_type="sync_missing",
                message="No successful sync recorded yet",
            )
            return self.upsert_state(db, shop_id=shop.shop_id, component=f"sync:{source_api}", status="warn")

        lag_seconds = int((now - sync.last_success_at).total_seconds())
        status = "ok" if sync.last_success_at >= now - timedelta(hours=stale_after_hours) else "warn"
        if status == "warn":
            self.write_event(
                db,
                shop_id=shop.shop_id,
                component=f"sync:{source_api}",
                severity="warn",
                event_type="stale_sync",
                message="Sync is stale",
                payload={"lag_seconds": lag_seconds},
            )
        return self.upsert_state(
            db,
            shop_id=shop.shop_id,
            component=f"sync:{source_api}",
            status=status,
            last_success_at=sync.last_success_at,
            lag_seconds=lag_seconds,
        )

    def check_stuck_drafts(self, db: Session, shop: Shop, older_than_hours: int = 24) -> HealthState:
        threshold = datetime.now(UTC) - timedelta(hours=older_than_hours)
        stmt = select(func.count()).select_from(ReplyDraft).where(
            ReplyDraft.shop_id == shop.shop_id,
            ReplyDraft.created_at < threshold,
            ReplyDraft.status == "generated",
        )
        count = db.execute(stmt).scalar_one()
        status = "ok" if count == 0 else "warn"
        if count:
            self.write_event(
                db,
                shop_id=shop.shop_id,
                component="drafts",
                severity="warn",
                event_type="stuck_drafts",
                message="Generated drafts waiting too long",
                payload={"count": count},
            )
        return self.upsert_state(db, shop_id=shop.shop_id, component="drafts", status=status, lag_seconds=None)

    def check_publish_failures(self, db: Session, shop: Shop) -> HealthState:
        since = datetime.now(UTC) - timedelta(hours=24)
        stmt = select(func.count()).select_from(ReplyPublication).where(
            ReplyPublication.shop_id == shop.shop_id,
            ReplyPublication.published_at.is_(None),
            ReplyPublication.error_text.is_not(None),
        )
        count = db.execute(stmt).scalar_one()
        status = "ok" if count == 0 else "error"
        return self.upsert_state(
            db,
            shop_id=shop.shop_id,
            component="publish",
            status=status,
            error_count_24h=count,
            last_error_at=datetime.now(UTC) if count else None,
        )

    def check_media_backlog(self, db: Session, shop: Shop) -> HealthState:
        stmt = select(func.count()).select_from(FeedbackMedia).where(
            FeedbackMedia.shop_id == shop.shop_id,
            FeedbackMedia.vision_status.is_(None),
        )
        count = db.execute(stmt).scalar_one()
        status = "ok" if count == 0 else "warn"
        return self.upsert_state(
            db,
            shop_id=shop.shop_id,
            component="media",
            status=status,
            lag_seconds=None,
            error_count_24h=0,
        )

    def operator_queries(self) -> dict[str, str]:
        return {
            "latest_health_state": "SELECT * FROM health_state ORDER BY updated_at DESC;",
            "recent_health_events": "SELECT * FROM health_events ORDER BY created_at DESC LIMIT 100;",
            "stale_syncs": "SELECT * FROM health_state WHERE component LIKE 'sync:%' AND status <> 'ok';",
            "stuck_drafts": "SELECT * FROM reply_drafts WHERE status = 'generated' ORDER BY created_at ASC;",
            "publish_failures": "SELECT * FROM reply_publications WHERE error_text IS NOT NULL ORDER BY id DESC;",
            "media_backlog": "SELECT * FROM feedback_media WHERE vision_status IS NULL ORDER BY id ASC;",
        }
