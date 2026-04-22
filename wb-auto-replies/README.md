# wb-auto-replies

Модульная code-first система автоматической обработки отзывов Wildberries для нескольких магазинов.

## Цели

- загружать исторические и новые отзывы WB в PostgreSQL
- различать кармические и реальные отзывы
- генерировать безопасные ответы по правилам и GPT
- поддерживать dry-run/draft режим до боевой публикации
- публиковать ответы в WB только в production mode
- хранить историю входных данных, драфтов, публикаций и состояния системы
- давать понятный health monitoring через таблицы БД

## Принципы

- ядро системы в коде, не в visual workflow
- модульная архитектура
- PostgreSQL как source of truth
- сначала безопасный draft pipeline, потом production publish
- явные режимы работы: `backfill`, `draft`, `publish`

## Документы

- `docs/01-product-overview.md`
- `docs/02-architecture.md`
- `docs/03-data-model.md`
- `docs/04-jobs-and-flows.md`
- `docs/05-implementation-plan.md`
- `checklists/implementation-checklist.md`
- `checklists/launch-readiness.md`

## Предлагаемый стек

- Python service/jobs
- PostgreSQL
- OpenAI-compatible GPT provider
- optional scheduler: cron/systemd/OpenClaw cron

## Статус

Проект открыт. Сейчас этап: реализация core foundation и safe dry-run pipeline.

## CLI jobs

После установки проекта доступны команды:

- `wb-auto-replies backfill --shop-id <id>`
- `wb-auto-replies draft --shop-id <id>`
- `wb-auto-replies publish --shop-id <id>`
- `wb-auto-replies-seed --shop-name <name> --wb-token <token> --mode draft --gpt-model gpt-4.1-mini`

Параметры оркестрации (`batch_size`, `max_total`, `start_skip`) читаются системой из `shops.settings_json`.

Важно: текущий `publish` работает в safe dry-run режиме и не отправляет реальные ответы в WB.

При `429 Too Many Requests` со стороны WB клиент делает до 3 попыток с паузой 3 секунды. Если лимит не отпускает, ingest/backfill завершает шаг мягко: пишет `sync_state` и `health_event`, не делает грубый crash процесса. Между batch-запросами backfill тоже выдерживается пауза 3 секунды.
