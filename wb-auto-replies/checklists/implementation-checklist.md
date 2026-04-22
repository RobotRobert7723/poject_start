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
- [x] implement name safety analysis
- [x] implement strict fallback to `Здравствуйте!` on any name uncertainty
- [x] implement safe salutation generation
- [x] support parent/child feedback links
- [x] support feedback versioning/is_latest
- [x] detect changed feedbacks and mark for regeneration
- [x] detect photo/video presence
- [x] persist media metadata

## Draft generation
- [x] implement karmic reply rules lookup
- [x] generate karmic drafts without GPT
- [x] implement article context lookup (last 10 reviews)
- [x] implement semantic template lookup
- [x] design GPT prompt contract
- [x] implement GPT draft generation for real reviews
- [x] save prompt/context snapshots
- [x] add response validation rules
- [x] add anti-repeat safeguards
- [x] ensure draft pipeline can run in debug/dry-run mode without WB publication

## Media analysis
- [ ] design vision summary contract
- [ ] implement photo analysis flow
- [ ] persist vision summary and confidence
- [ ] include media summary in GPT context

## Publish pipeline
- [ ] implement WB answer publish client
- [ ] implement draft eligibility checks
- [ ] implement latest-version-only publish checks
- [ ] implement publish mode gating
- [ ] implement retry/error handling
- [ ] persist publication audit trail
- [ ] prevent duplicate publish behavior

## Health monitoring
- [ ] define health metrics per component
- [ ] implement health event writer
- [ ] implement health state updater
- [ ] detect stale syncs
- [ ] detect stuck drafts
- [ ] detect publish failures
- [ ] detect media analysis backlog
- [ ] prepare basic operator SQL queries

## Readiness
- [ ] run end-to-end in backfill mode
- [ ] run end-to-end in draft mode
- [ ] verify no publish in draft mode
- [ ] verify publish path in controlled test
- [ ] validate multi-store isolation
