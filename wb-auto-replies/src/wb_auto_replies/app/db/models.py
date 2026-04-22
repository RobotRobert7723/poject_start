from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from wb_auto_replies.app.db.base import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class Shop(TimestampMixin, Base):
    __tablename__ = "shops"

    shop_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shop_name: Mapped[str] = mapped_column(String(255), nullable=False)
    wb_token: Mapped[str] = mapped_column(Text, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    mode: Mapped[str] = mapped_column(String(32), nullable=False)
    gpt_model: Mapped[str | None] = mapped_column(String(128), nullable=True)
    settings_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)


class FeedbackRaw(Base):
    __tablename__ = "feedbacks_raw"
    __table_args__ = (
        Index("ix_feedbacks_raw_shop_source_fetched", "shop_id", "source_api", "fetched_at"),
        UniqueConstraint("shop_id", "source_api", "feedback_id", "source_hash", name="uq_feedbacks_raw_source_hash"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shop_id: Mapped[int] = mapped_column(ForeignKey("shops.shop_id"), nullable=False)
    source_api: Mapped[str] = mapped_column(String(32), nullable=False)
    feedback_id: Mapped[str] = mapped_column(String(128), nullable=False)
    payload_json: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    source_hash: Mapped[str] = mapped_column(String(128), nullable=False)


class Feedback(TimestampMixin, Base):
    __tablename__ = "feedbacks"
    __table_args__ = (
        UniqueConstraint("shop_id", "feedback_id", "version_no", name="uq_feedbacks_shop_feedback_version"),
        Index("ix_feedbacks_shop_nm_created", "shop_id", "nm_id", "created_date"),
        Index("ix_feedbacks_shop_kind_processing", "shop_id", "feedback_kind", "processing_status"),
        Index("ix_feedbacks_shop_latest", "shop_id", "is_latest"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shop_id: Mapped[int] = mapped_column(ForeignKey("shops.shop_id"), nullable=False)
    feedback_id: Mapped[str] = mapped_column(String(128), nullable=False)
    feedback_thread_key: Mapped[str | None] = mapped_column(String(128), nullable=True)
    version_no: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    is_latest: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    source_api: Mapped[str] = mapped_column(String(32), nullable=False)
    feedback_kind: Mapped[str] = mapped_column(String(32), nullable=False, default="unknown")
    created_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    stars: Mapped[int | None] = mapped_column(Integer, nullable=True)
    text: Mapped[str | None] = mapped_column(Text, nullable=True)
    pros: Mapped[str | None] = mapped_column(Text, nullable=True)
    cons: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_name_raw: Mapped[str | None] = mapped_column(String(255), nullable=True)
    safe_salutation: Mapped[str | None] = mapped_column(String(255), nullable=True)
    safe_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    name_confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    has_photo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    has_video: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    nm_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    imt_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    product_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    supplier_article: Mapped[str | None] = mapped_column(String(255), nullable=True)
    brand_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    subject_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    subject_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    parent_feedback_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    child_feedback_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    answer_text_current: Mapped[str | None] = mapped_column(Text, nullable=True)
    answer_state_current: Mapped[str | None] = mapped_column(String(64), nullable=True)
    processing_status: Mapped[str] = mapped_column(String(64), nullable=False, default="normalized")
    needs_regeneration: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    media_items: Mapped[list[FeedbackMedia]] = relationship(back_populates="feedback")


class FeedbackMedia(Base):
    __tablename__ = "feedback_media"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shop_id: Mapped[int] = mapped_column(ForeignKey("shops.shop_id"), nullable=False)
    feedback_id: Mapped[int] = mapped_column(ForeignKey("feedbacks.id"), nullable=False)
    media_type: Mapped[str] = mapped_column(String(32), nullable=False)
    media_url: Mapped[str] = mapped_column(Text, nullable=False)
    vision_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    vision_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    vision_confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 4), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    feedback: Mapped[Feedback] = relationship(back_populates="media_items")


class SemanticReplyTemplate(TimestampMixin, Base):
    __tablename__ = "semantic_reply_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shop_id: Mapped[int | None] = mapped_column(ForeignKey("shops.shop_id"), nullable=True)
    category_key: Mapped[str] = mapped_column(String(128), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    template_text: Mapped[str] = mapped_column(Text, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=100)


class KarmicReplyRule(TimestampMixin, Base):
    __tablename__ = "karmic_reply_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shop_id: Mapped[int] = mapped_column(ForeignKey("shops.shop_id"), nullable=False)
    stars_from: Mapped[int] = mapped_column(Integer, nullable=False)
    stars_to: Mapped[int] = mapped_column(Integer, nullable=False)
    reply_text: Mapped[str] = mapped_column(Text, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class ReplyDraft(Base):
    __tablename__ = "reply_drafts"
    __table_args__ = (
        Index("ix_reply_drafts_shop_feedback_created", "shop_id", "feedback_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shop_id: Mapped[int] = mapped_column(ForeignKey("shops.shop_id"), nullable=False)
    feedback_id: Mapped[int] = mapped_column(ForeignKey("feedbacks.id"), nullable=False)
    feedback_version_no: Mapped[int] = mapped_column(Integer, nullable=False)
    generator_type: Mapped[str] = mapped_column(String(32), nullable=False)
    mode: Mapped[str] = mapped_column(String(32), nullable=False)
    prompt_snapshot: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    context_snapshot: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    draft_text: Mapped[str] = mapped_column(Text, nullable=False)
    quality_flags_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ReplyPublication(Base):
    __tablename__ = "reply_publications"
    __table_args__ = (
        Index("ix_reply_publications_shop_feedback_published", "shop_id", "feedback_id", "published_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shop_id: Mapped[int] = mapped_column(ForeignKey("shops.shop_id"), nullable=False)
    feedback_id: Mapped[int] = mapped_column(ForeignKey("feedbacks.id"), nullable=False)
    draft_id: Mapped[int] = mapped_column(ForeignKey("reply_drafts.id"), nullable=False)
    published_text: Mapped[str] = mapped_column(Text, nullable=False)
    wb_response_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    publish_status: Mapped[str] = mapped_column(String(32), nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_text: Mapped[str | None] = mapped_column(Text, nullable=True)


class SyncState(Base):
    __tablename__ = "sync_state"
    __table_args__ = (
        UniqueConstraint("shop_id", "source_api", name="uq_sync_state_shop_source_api"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shop_id: Mapped[int] = mapped_column(ForeignKey("shops.shop_id"), nullable=False)
    source_api: Mapped[str] = mapped_column(String(32), nullable=False)
    last_success_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_attempt_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_cursor_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    last_error_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    stats_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)


class HealthEvent(Base):
    __tablename__ = "health_events"
    __table_args__ = (
        Index("ix_health_events_component_created", "component", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shop_id: Mapped[int | None] = mapped_column(ForeignKey("shops.shop_id"), nullable=True)
    component: Mapped[str] = mapped_column(String(64), nullable=False)
    severity: Mapped[str] = mapped_column(String(16), nullable=False)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    payload_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class HealthState(Base):
    __tablename__ = "health_state"
    __table_args__ = (
        UniqueConstraint("shop_id", "component", name="uq_health_state_shop_component"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    shop_id: Mapped[int | None] = mapped_column(ForeignKey("shops.shop_id"), nullable=True)
    component: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    last_success_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_error_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_count_24h: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    lag_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
