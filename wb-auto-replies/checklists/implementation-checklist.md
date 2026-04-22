# Implementation Checklist

## Project setup
- [ ] confirm final tech stack (Python recommended)
- [ ] choose packaging/dependency tool
- [ ] create app skeleton
- [ ] create environment variable strategy
- [ ] choose migrations tool

## Database
- [ ] create initial schema
- [ ] create shops table
- [ ] create feedbacks_raw table
- [ ] create feedbacks table
- [ ] create feedback_media table
- [ ] create sync_state table
- [ ] create reply_drafts table
- [ ] create reply_publications table
- [ ] create karmic_reply_rules table
- [ ] create semantic_reply_templates table
- [ ] create health_events table
- [ ] create health_state table
- [ ] add indexes and constraints

## WB integration
- [ ] implement archive feedback API client
- [ ] implement active feedback API client
- [ ] implement retry policy
- [ ] implement WB rate-limit handling
- [ ] persist raw payloads
- [ ] normalize archive feedbacks
- [ ] normalize active feedbacks
- [ ] implement sync state storage
- [ ] prove idempotent re-run behavior

## Classification and enrichment
- [ ] implement karmic vs real classification
- [ ] implement name safety analysis
- [ ] implement safe salutation generation
- [ ] support parent/child feedback links
- [ ] support feedback versioning/is_latest
- [ ] detect photo/video presence
- [ ] persist media metadata

## Draft generation
- [ ] implement karmic reply rules lookup
- [ ] generate karmic drafts without GPT
- [ ] implement article context lookup (last 10 reviews)
- [ ] implement semantic template lookup
- [ ] design GPT prompt contract
- [ ] implement GPT draft generation for real reviews
- [ ] save prompt/context snapshots
- [ ] add response validation rules
- [ ] add anti-repeat safeguards

## Media analysis
- [ ] design vision summary contract
- [ ] implement photo analysis flow
- [ ] persist vision summary and confidence
- [ ] include media summary in GPT context

## Publish pipeline
- [ ] implement WB answer publish client
- [ ] implement draft eligibility checks
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
- [ ] prepare basic operator SQL queries

## Readiness
- [ ] run end-to-end in backfill mode
- [ ] run end-to-end in draft mode
- [ ] verify no publish in draft mode
- [ ] verify publish path in controlled test
- [ ] validate multi-store isolation
