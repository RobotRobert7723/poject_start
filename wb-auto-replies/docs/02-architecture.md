# Architecture

## Архитектурный подход

Система строится как **code-first modular backend**, где бизнес-логика живет в коде, а не в workflow-конструкторе.

## High-level components

### 1. Configuration / Shop Management

Отвечает за:
- список магазинов
- токены WB
- режимы запуска
- GPT settings
- политики публикации
- шаблоны/правила

### 2. WB API Integration

Два независимых клиента:
- `archive client` для кармических/архивных отзывов
- `active client` для реальных/свежих отзывов

Функции:
- pagination
- retry policy
- rate limits
- raw payload capture
- watermark/cursor support

### 3. Storage Layer

PostgreSQL как единый источник истины.

Хранит:
- raw events
- normalized feedbacks
- reply drafts
- publications
- sync state
- health records

### 4. Processing / Enrichment Layer

Модули:
- classifier
- name guard
- media analyzer
- context builder
- template selector

### 5. Reply Generation Layer

Два независимых пути:

#### Template path
Для кармических отзывов:
- без GPT
- по правилам и настройкам

#### GPT path
Для реальных отзывов:
- с article context
- с semantic templates
- с media summary
- с guardrails

### 6. Publication Layer

Отвечает за:
- draft-only pipeline
- publish pipeline
- audit trail
- retry and failure handling

### 7. Health Monitoring Layer

Отвечает за:
- health checks per job
- pipeline lag
- error counts
- stuck items
- publication failures

## Logical modules

```text
wb_auto_replies/
  app/
    config/
    db/
    wb/
      archive_client.py
      active_client.py
    ingest/
    classifier/
    names/
    media/
    context/
    templates/
    gpt/
    drafts/
    publish/
    health/
    jobs/
```

## Execution model

Система должна быть разбита на независимые jobs:

1. `backfill_archive_job`
2. `sync_active_feedbacks_job`
3. `enrich_feedbacks_job`
4. `generate_drafts_job`
5. `publish_replies_job`
6. `health_check_job`

## Why not one monolith job

Причины:
- проще дебажить
- проще перезапускать частично
- проще измерять lag
- проще мониторить здоровье
- проще запускать в draft/publish режимах

## Main design rules

### Rule 1. Ingest is separate from generation
Никогда не смешивать загрузку отзывов с генерацией ответа в один неразделимый шаг.

### Rule 2. Draft is separate from publish
Draft pipeline обязателен.

### Rule 3. Raw payload is preserved
Сохранять исходный ответ WB API для дебага и повторной нормализации.

### Rule 4. Every important step is auditable
Каждая генерация и публикация должна быть восстановима по истории.

### Rule 5. Store state explicitly
Все курсоры, watermark-и, статусы и health-события должны быть в БД.

## Suggested runtime

- Python 3.12+
- PostgreSQL
- CLI jobs for scheduled execution
- scheduler outside core app: system cron, systemd timer, or OpenClaw cron

## Future-friendly extensions

- admin UI for draft review
- manual moderation queue
- analytics dashboard
- fine-grained prompt/version experiments
- queue system if load grows
