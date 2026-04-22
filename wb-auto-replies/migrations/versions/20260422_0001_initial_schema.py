"""initial schema

revision = '20260422_0001'
down_revision = None
branch_labels = None
depends_on = None
"""

from alembic import op
import sqlalchemy as sa


revision = "20260422_0001"
down_revision = None
branch_labels = None
depends_on = None
SCHEMA = "wb_auto_replies"


def upgrade() -> None:
    op.execute(f"CREATE SCHEMA IF NOT EXISTS {SCHEMA}")

    op.create_table(
        "shops",
        sa.Column("shop_id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("shop_name", sa.String(length=255), nullable=False),
        sa.Column("wb_token", sa.Text(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("mode", sa.String(length=32), nullable=False),
        sa.Column("gpt_model", sa.String(length=128), nullable=True),
        sa.Column("settings_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        schema=SCHEMA,
    )

    op.create_table(
        "feedbacks_raw",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("shop_id", sa.Integer(), sa.ForeignKey(f"{SCHEMA}.shops.shop_id"), nullable=False),
        sa.Column("source_api", sa.String(length=32), nullable=False),
        sa.Column("feedback_id", sa.String(length=128), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("source_hash", sa.String(length=128), nullable=False),
        sa.UniqueConstraint("shop_id", "source_api", "feedback_id", "source_hash", name="uq_feedbacks_raw_source_hash"),
        schema=SCHEMA,
    )
    op.create_index("ix_feedbacks_raw_shop_source_fetched", "feedbacks_raw", ["shop_id", "source_api", "fetched_at"], schema=SCHEMA)

    op.create_table(
        "feedbacks",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("shop_id", sa.Integer(), sa.ForeignKey(f"{SCHEMA}.shops.shop_id"), nullable=False),
        sa.Column("feedback_id", sa.String(length=128), nullable=False),
        sa.Column("feedback_thread_key", sa.String(length=128), nullable=True),
        sa.Column("version_no", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_latest", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("source_api", sa.String(length=32), nullable=False),
        sa.Column("feedback_kind", sa.String(length=32), nullable=False, server_default="unknown"),
        sa.Column("created_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("stars", sa.Integer(), nullable=True),
        sa.Column("text", sa.Text(), nullable=True),
        sa.Column("pros", sa.Text(), nullable=True),
        sa.Column("cons", sa.Text(), nullable=True),
        sa.Column("user_name_raw", sa.String(length=255), nullable=True),
        sa.Column("safe_salutation", sa.String(length=255), nullable=True),
        sa.Column("safe_name", sa.String(length=255), nullable=True),
        sa.Column("name_confidence", sa.Numeric(5, 4), nullable=True),
        sa.Column("has_photo", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("has_video", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("nm_id", sa.Integer(), nullable=True),
        sa.Column("imt_id", sa.Integer(), nullable=True),
        sa.Column("product_name", sa.String(length=255), nullable=True),
        sa.Column("supplier_article", sa.String(length=255), nullable=True),
        sa.Column("brand_name", sa.String(length=255), nullable=True),
        sa.Column("subject_id", sa.Integer(), nullable=True),
        sa.Column("subject_name", sa.String(length=255), nullable=True),
        sa.Column("parent_feedback_id", sa.String(length=128), nullable=True),
        sa.Column("child_feedback_id", sa.String(length=128), nullable=True),
        sa.Column("answer_text_current", sa.Text(), nullable=True),
        sa.Column("answer_state_current", sa.String(length=64), nullable=True),
        sa.Column("processing_status", sa.String(length=64), nullable=False, server_default="normalized"),
        sa.Column("needs_regeneration", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("shop_id", "feedback_id", "version_no", name="uq_feedbacks_shop_feedback_version"),
        schema=SCHEMA,
    )
    op.create_index("ix_feedbacks_shop_nm_created", "feedbacks", ["shop_id", "nm_id", "created_date"], schema=SCHEMA)
    op.create_index("ix_feedbacks_shop_kind_processing", "feedbacks", ["shop_id", "feedback_kind", "processing_status"], schema=SCHEMA)
    op.create_index("ix_feedbacks_shop_latest", "feedbacks", ["shop_id", "is_latest"], schema=SCHEMA)

    op.create_table(
        "feedback_media",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("shop_id", sa.Integer(), sa.ForeignKey(f"{SCHEMA}.shops.shop_id"), nullable=False),
        sa.Column("feedback_id", sa.Integer(), sa.ForeignKey(f"{SCHEMA}.feedbacks.id"), nullable=False),
        sa.Column("media_type", sa.String(length=32), nullable=False),
        sa.Column("media_url", sa.Text(), nullable=False),
        sa.Column("vision_status", sa.String(length=32), nullable=True),
        sa.Column("vision_summary", sa.Text(), nullable=True),
        sa.Column("vision_confidence", sa.Numeric(5, 4), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        schema=SCHEMA,
    )

    op.create_table(
        "semantic_reply_templates",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("shop_id", sa.Integer(), sa.ForeignKey(f"{SCHEMA}.shops.shop_id"), nullable=True),
        sa.Column("category_key", sa.String(length=128), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("template_text", sa.Text(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="100"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        schema=SCHEMA,
    )

    op.create_table(
        "karmic_reply_rules",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("shop_id", sa.Integer(), sa.ForeignKey(f"{SCHEMA}.shops.shop_id"), nullable=False),
        sa.Column("stars_from", sa.Integer(), nullable=False),
        sa.Column("stars_to", sa.Integer(), nullable=False),
        sa.Column("reply_text", sa.Text(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        schema=SCHEMA,
    )

    op.create_table(
        "reply_drafts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("shop_id", sa.Integer(), sa.ForeignKey(f"{SCHEMA}.shops.shop_id"), nullable=False),
        sa.Column("feedback_id", sa.Integer(), sa.ForeignKey(f"{SCHEMA}.feedbacks.id"), nullable=False),
        sa.Column("feedback_version_no", sa.Integer(), nullable=False),
        sa.Column("generator_type", sa.String(length=32), nullable=False),
        sa.Column("mode", sa.String(length=32), nullable=False),
        sa.Column("prompt_snapshot", sa.JSON(), nullable=True),
        sa.Column("context_snapshot", sa.JSON(), nullable=True),
        sa.Column("draft_text", sa.Text(), nullable=False),
        sa.Column("quality_flags_json", sa.JSON(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        schema=SCHEMA,
    )
    op.create_index("ix_reply_drafts_shop_feedback_created", "reply_drafts", ["shop_id", "feedback_id", "created_at"], schema=SCHEMA)

    op.create_table(
        "reply_publications",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("shop_id", sa.Integer(), sa.ForeignKey(f"{SCHEMA}.shops.shop_id"), nullable=False),
        sa.Column("feedback_id", sa.Integer(), sa.ForeignKey(f"{SCHEMA}.feedbacks.id"), nullable=False),
        sa.Column("draft_id", sa.Integer(), sa.ForeignKey(f"{SCHEMA}.reply_drafts.id"), nullable=False),
        sa.Column("published_text", sa.Text(), nullable=False),
        sa.Column("wb_response_json", sa.JSON(), nullable=True),
        sa.Column("publish_status", sa.String(length=32), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_text", sa.Text(), nullable=True),
        schema=SCHEMA,
    )
    op.create_index("ix_reply_publications_shop_feedback_published", "reply_publications", ["shop_id", "feedback_id", "published_at"], schema=SCHEMA)

    op.create_table(
        "sync_state",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("shop_id", sa.Integer(), sa.ForeignKey(f"{SCHEMA}.shops.shop_id"), nullable=False),
        sa.Column("source_api", sa.String(length=32), nullable=False),
        sa.Column("last_success_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_attempt_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_cursor_json", sa.JSON(), nullable=True),
        sa.Column("last_error_text", sa.Text(), nullable=True),
        sa.Column("stats_json", sa.JSON(), nullable=True),
        sa.UniqueConstraint("shop_id", "source_api", name="uq_sync_state_shop_source_api"),
        schema=SCHEMA,
    )

    op.create_table(
        "health_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("shop_id", sa.Integer(), sa.ForeignKey(f"{SCHEMA}.shops.shop_id"), nullable=True),
        sa.Column("component", sa.String(length=64), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("payload_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        schema=SCHEMA,
    )
    op.create_index("ix_health_events_component_created", "health_events", ["component", "created_at"], schema=SCHEMA)

    op.create_table(
        "health_state",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("shop_id", sa.Integer(), sa.ForeignKey(f"{SCHEMA}.shops.shop_id"), nullable=True),
        sa.Column("component", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("last_success_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_count_24h", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("lag_seconds", sa.Integer(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("shop_id", "component", name="uq_health_state_shop_component"),
        schema=SCHEMA,
    )


def downgrade() -> None:
    op.drop_table("health_state", schema=SCHEMA)
    op.drop_index("ix_health_events_component_created", table_name="health_events", schema=SCHEMA)
    op.drop_table("health_events", schema=SCHEMA)
    op.drop_table("sync_state", schema=SCHEMA)
    op.drop_index("ix_reply_publications_shop_feedback_published", table_name="reply_publications", schema=SCHEMA)
    op.drop_table("reply_publications", schema=SCHEMA)
    op.drop_index("ix_reply_drafts_shop_feedback_created", table_name="reply_drafts", schema=SCHEMA)
    op.drop_table("reply_drafts", schema=SCHEMA)
    op.drop_table("karmic_reply_rules", schema=SCHEMA)
    op.drop_table("semantic_reply_templates", schema=SCHEMA)
    op.drop_table("feedback_media", schema=SCHEMA)
    op.drop_index("ix_feedbacks_shop_latest", table_name="feedbacks", schema=SCHEMA)
    op.drop_index("ix_feedbacks_shop_kind_processing", table_name="feedbacks", schema=SCHEMA)
    op.drop_index("ix_feedbacks_shop_nm_created", table_name="feedbacks", schema=SCHEMA)
    op.drop_table("feedbacks", schema=SCHEMA)
    op.drop_index("ix_feedbacks_raw_shop_source_fetched", table_name="feedbacks_raw", schema=SCHEMA)
    op.drop_table("feedbacks_raw", schema=SCHEMA)
    op.drop_table("shops", schema=SCHEMA)
    op.execute(f"DROP SCHEMA IF EXISTS {SCHEMA} CASCADE")
