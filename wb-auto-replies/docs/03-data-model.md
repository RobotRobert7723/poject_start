# Data Model

## Core tables

### shops

Purpose: настройки и режимы магазина.

Suggested fields:
- `shop_id` PK
- `shop_name`
- `wb_token`
- `active`
- `mode` (`backfill|draft|publish`)
- `gpt_model`
- `settings_json`
- `created_at`
- `updated_at`

### feedbacks_raw

Purpose: сырой payload WB для архива и новых отзывов.

Suggested fields:
- `id` PK
- `shop_id`
- `source_api` (`archive|active`)
- `feedback_id`
- `payload_json`
- `fetched_at`
- `source_hash`

### feedbacks

Purpose: нормализованная модель отзыва.

Suggested fields:
- `id` PK
- `shop_id`
- `feedback_id`
- `feedback_thread_key`
- `version_no`
- `is_latest`
- `source_api`
- `feedback_kind` (`karmic|real|unknown`)
- `created_date`
- `updated_date`
- `stars`
- `text`
- `pros`
- `cons`
- `user_name_raw`
- `safe_salutation`
- `safe_name`
- `name_confidence`
- `has_photo`
- `has_video`
- `nm_id`
- `imt_id`
- `product_name`
- `supplier_article`
- `brand_name`
- `subject_id`
- `subject_name`
- `parent_feedback_id`
- `child_feedback_id`
- `answer_text_current`
- `answer_state_current`
- `processing_status`
- `needs_regeneration`
- `created_at`
- `updated_at`

Key constraints:
- unique `(shop_id, feedback_id, version_no)`
- partial uniqueness for latest version if needed

### feedback_media

Purpose: медиа и анализ изображений.

Suggested fields:
- `id` PK
- `shop_id`
- `feedback_id`
- `media_type`
- `media_url`
- `vision_status`
- `vision_summary`
- `vision_confidence`
- `created_at`

### semantic_reply_templates

Purpose: типовые ответы по смысловым категориям.

Suggested fields:
- `id` PK
- `shop_id` nullable
- `category_key`
- `title`
- `description`
- `template_text`
- `active`
- `priority`
- `created_at`
- `updated_at`

### karmic_reply_rules

Purpose: шаблоны для кармических отзывов.

Suggested fields:
- `id` PK
- `shop_id`
- `stars_from`
- `stars_to`
- `reply_text`
- `active`
- `created_at`
- `updated_at`

### reply_drafts

Purpose: история draft-ответов.

Suggested fields:
- `id` PK
- `shop_id`
- `feedback_id`
- `feedback_version_no`
- `generator_type` (`template|gpt`)
- `mode` (`draft|publish`)
- `prompt_snapshot`
- `context_snapshot`
- `draft_text`
- `quality_flags_json`
- `status`
- `created_at`

### reply_publications

Purpose: история реальных публикаций.

Suggested fields:
- `id` PK
- `shop_id`
- `feedback_id`
- `draft_id`
- `published_text`
- `wb_response_json`
- `publish_status`
- `published_at`
- `error_text`

### sync_state

Purpose: курсоры и состояние синхронизации.

Suggested fields:
- `shop_id`
- `source_api`
- `last_success_at`
- `last_attempt_at`
- `last_cursor_json`
- `last_error_text`
- `stats_json`

### health_events

Purpose: журнал здоровья системы.

Suggested fields:
- `id` PK
- `shop_id` nullable
- `component`
- `severity` (`info|warn|error`)
- `event_type`
- `message`
- `payload_json`
- `created_at`

### health_state

Purpose: последняя health-сводка по компонентам.

Suggested fields:
- `shop_id`
- `component`
- `status`
- `last_success_at`
- `last_error_at`
- `error_count_24h`
- `lag_seconds`
- `updated_at`

## Recommended indexes

- `feedbacks(shop_id, nm_id, created_date desc)`
- `feedbacks(shop_id, feedback_kind, processing_status)`
- `feedbacks(shop_id, is_latest)`
- `feedbacks_raw(shop_id, source_api, fetched_at desc)`
- `reply_drafts(shop_id, feedback_id, created_at desc)`
- `reply_publications(shop_id, feedback_id, published_at desc)`
- `health_events(component, created_at desc)`
- `sync_state(shop_id, source_api)` unique

## Data retention notes

- raw payloads useful for debugging and reparsing
- drafts must be retained for auditability
- publications must be immutable audit records
- health events can later be compacted/archived if volume grows
