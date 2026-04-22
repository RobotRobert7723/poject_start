# Jobs and Flows

## Job 1. backfill_archive_job

### Goal
Загрузить исторические архивные/кармические данные в БД.

### Inputs
- shop config
- WB archive API token
- initial cursor/date strategy

### Outputs
- `feedbacks_raw`
- `feedbacks`
- `sync_state`
- `health_events`

### Notes
- archive API and active API are separate
- must respect WB rate limits
- no publish actions in this job

## Job 2. sync_active_feedbacks_job

### Goal
Регулярно загружать новые реальные отзывы.

### Inputs
- active feedback API
- per-shop sync cursor/state

### Outputs
- `feedbacks_raw`
- `feedbacks`
- `sync_state`
- health records

### Schedule
Несколько раз в день, configurable per shop.

## Job 3. enrich_feedbacks_job

### Goal
Подготовить отзывы к генерации ответа.

### Steps
- classify feedback kind
- analyze name safety
- detect media and prepare media tasks
- mark processing status
- set regeneration flags for changed feedbacks

### Outputs
- updated `feedbacks`
- `feedback_media`
- `health_events`

## Job 4. analyze_media_job

### Goal
Для отзывов с фото получить компактный vision summary.

### Outputs
- `feedback_media.vision_summary`
- confidence and status

## Job 5. generate_drafts_job

### Goal
Создать draft-ответы.

### Branches

#### Karmic branch
- no GPT
- select rule from `karmic_reply_rules`
- save draft

#### Real branch
- get last 10 reviews by article
- get semantic templates by meaning
- build prompt context
- generate GPT answer
- validate result
- save draft

### Outputs
- `reply_drafts`
- `health_events`

## Job 6. publish_replies_job

### Goal
Публиковать ответы только для магазинов в publish mode.

### Preconditions
- shop mode = `publish`
- draft exists and is valid
- feedback is still relevant/latest

### Outputs
- `reply_publications`
- update current answer fields in `feedbacks`
- `health_events`

## Job 7. health_check_job

### Goal
Формировать простую health-сводку в БД.

### Checks
- last successful archive sync
- last successful active sync
- lag on active feedbacks
- pending items count
- drafts waiting too long
- publish failures
- media analysis backlog

### Outputs
- `health_state`
- `health_events`

## State machine for feedback processing

```text
new_raw
  -> normalized
  -> classified
  -> enriched
  -> draft_generated
  -> ready_for_publish
  -> published
```

Possible side states:
- `skipped`
- `needs_review`
- `failed`
- `stale`

## Environment modes

### backfill
- ingest only
- no generation if not needed yet
- no publish

### draft
- ingest + enrich + draft generation
- no publish

### publish
- full pipeline including publish

## Scheduling recommendation

- archive backfill: manual/one-shot or batched until complete
- active sync: several times per day
- enrich: after each sync or frequent small runs
- draft generation: after enrich
- publish: separate controlled run
- health: every 15-30 min

## Why separate publish job

- easier rollback
- easier dry-run
- safer production controls
- easier manual moderation extension later
