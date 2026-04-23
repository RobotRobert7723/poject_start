# Implementation Checklist

## Project setup
- [x] confirm final tech stack (Python recommended)
- [x] choose packaging/dependency tool
- [x] create app skeleton
- [x] create environment variable strategy
- [x] choose migrations tool

## Database
- [x] create initial schema
- [x] create shops table
- [x] create feedbacks_raw table
- [x] create feedbacks table
- [x] create feedback_media table
- [x] create sync_state table
- [x] create reply_drafts table
- [x] create reply_publications table
- [x] create karmic_reply_rules table
- [x] create semantic_reply_templates table
- [x] create health_events table
- [x] create health_state table
- [x] store raw WB payloads for both archive and active APIs
- [x] store current answer state and published answer history
- [x] add indexes and constraints

## WB integration
- [x] implement archive feedback API client
- [x] implement active feedback API client
- [x] implement retry policy
- [x] implement WB rate-limit handling
- [x] persist raw payloads
- [x] normalize archive feedbacks
- [x] normalize active feedbacks
- [x] implement separate sync cursor/state per shop and per API
- [x] implement sync state storage
- [x] prove idempotent re-run behavior
- [x] verify actual WB API field mapping against docs/examples

## Classification and enrichment
- [x] implement karmic vs real classification
- [x] fix karmic classification for active reviews with rating but empty `text/pros/cons`
- [x] implement name safety analysis
- [x] implement strict fallback to `Здравствуйте!` on any name uncertainty
- [x] disable latin-name personalization and other doubtful single-token names
- [x] implement safe salutation generation
- [x] support parent/child feedback links
- [x] support feedback versioning/is_latest
- [x] detect changed feedbacks and mark for regeneration
- [x] detect photo/video presence
- [x] persist media metadata

## Draft generation
- [x] implement karmic reply rules lookup
- [x] generate karmic drafts without GPT
- [x] prevent karmic draft generation when WB answer text already exists
- [x] implement article context lookup (last 10 reviews)
- [x] implement semantic template lookup
- [x] design GPT prompt contract
- [x] implement GPT draft generation for real reviews
- [x] save prompt/context snapshots
- [x] add response validation rules
- [x] add anti-repeat safeguards
- [x] ensure draft pipeline can run in debug/dry-run mode without WB publication

## Media analysis
- [x] design vision summary contract
- [x] implement photo analysis flow
- [x] persist vision summary and confidence
- [x] include media summary in GPT context

## Publish pipeline
- [x] implement WB answer publish client
- [x] implement draft eligibility checks
- [x] implement latest-version-only publish checks
- [x] implement publish mode gating
- [x] implement retry/error handling
- [x] persist publication audit trail
- [x] prevent duplicate publish behavior

## Health monitoring
- [x] define health metrics per component
- [x] implement health event writer
- [x] implement health state updater
- [x] detect stale syncs
- [x] detect stuck drafts
- [x] detect publish failures
- [x] detect media analysis backlog
- [x] prepare basic operator SQL queries

## Readiness
- [x] run end-to-end in backfill mode
- [x] run end-to-end in draft mode
- [x] verify no publish in draft mode
- [x] verify publish path in controlled test
- [x] validate multi-store isolation
