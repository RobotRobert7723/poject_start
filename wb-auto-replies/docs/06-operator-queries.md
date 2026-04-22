# Operator Queries

## Latest health state

```sql
SELECT * FROM health_state ORDER BY updated_at DESC;
```

## Recent health events

```sql
SELECT * FROM health_events ORDER BY created_at DESC LIMIT 100;
```

## Stale syncs

```sql
SELECT * FROM health_state WHERE component LIKE 'sync:%' AND status <> 'ok';
```

## Stuck drafts

```sql
SELECT * FROM reply_drafts WHERE status = 'generated' ORDER BY created_at ASC;
```

## Publish failures

```sql
SELECT * FROM reply_publications WHERE error_text IS NOT NULL ORDER BY id DESC;
```

## Media backlog

```sql
SELECT * FROM feedback_media WHERE vision_status IS NULL ORDER BY id ASC;
```
