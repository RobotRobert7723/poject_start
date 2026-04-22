# Implementation Plan

## Phase 0. Project setup

### Deliverables
- repository structure
- project docs
- implementation checklist
- coding conventions
- environment configuration strategy

## Phase 1. Database foundation

### Deliverables
- schema DDL
- migrations strategy
- initial tables:
  - shops
  - feedbacks_raw
  - feedbacks
  - feedback_media
  - sync_state
  - health_events
  - health_state
  - karmic_reply_rules
  - semantic_reply_templates
  - reply_drafts
  - reply_publications

### Done when
- schema applies cleanly on empty DB
- core indexes created
- test seed data can be inserted

## Phase 2. WB ingest

### Deliverables
- archive API client
- active feedback API client
- rate limit policy
- retry policy
- raw payload persistence
- normalization pipeline
- sync state persistence

### Done when
- archive history loads into DB
- active feedback sync loads fresh reviews into DB
- duplicates are prevented
- sync resumes from state safely

## Phase 3. Processing and enrichment

### Deliverables
- karmic vs real classifier
- name safety module
- changed feedback/version handling
- media metadata extraction
- processing state transitions

### Done when
- feedbacks consistently land in correct branch
- unsafe names fall back to `Здравствуйте!`
- media presence is captured
- changed reviews are versioned and linked

## Phase 4. Draft generation

### Deliverables
- karmic template path
- semantic template selection for real reviews
- article context builder (last 10 reviews)
- GPT reply generator
- response validation/guardrails
- draft persistence

### Done when
- karmic drafts are deterministic and correct
- real-review drafts use context and templates
- output is saved with prompt/context snapshot
- no publish occurs in this phase

## Phase 5. Publish pipeline

### Deliverables
- WB answer publication client
- publish eligibility rules
- retry/error handling
- publication audit trail

### Done when
- publish mode can post responses safely
- every publish action is recorded
- repeated publish of the same answer is prevented or controlled

## Phase 6. Monitoring and operations

### Deliverables
- DB-based health summary
- lag metrics
- stuck item detection
- simple operational SQL views/queries

### Done when
- operator can understand system health from DB alone
- broken jobs and lagging syncs are visible quickly

## Recommended development order

1. schema and migrations
2. shops/settings model
3. archive ingest
4. active ingest
5. normalization + sync state
6. classifier + name guard
7. karmic template draft generation
8. real-review GPT draft generation
9. media analysis
10. publish pipeline
11. health monitoring

## Non-functional requirements

- idempotent syncs
- auditable write paths
- safe draft-before-publish flow
- modular code with job isolation
- clear error logging and recovery
