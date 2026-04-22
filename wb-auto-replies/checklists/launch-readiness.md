# Launch Readiness Checklist

## Before first draft launch
- [ ] DB schema applied in target environment
- [ ] all required shops configured
- [ ] WB tokens verified
- [ ] archive and active APIs tested manually
- [ ] separate archive and active sync states verified
- [ ] draft mode enabled for all shops
- [ ] debug/dry-run path verified end-to-end
- [ ] karmic templates filled
- [ ] semantic templates seeded
- [ ] GPT provider credentials configured
- [ ] prompt and safety rules reviewed
- [ ] strict name-safety fallback behavior reviewed
- [ ] health tables updating correctly

## Before first publish launch
- [ ] draft pipeline stable for several runs
- [ ] draft quality manually reviewed
- [ ] name safety fallback verified
- [ ] media analysis checked on real examples
- [ ] feedback versioning behavior verified
- [ ] publish only latest feedback version
- [ ] publish client tested in controlled scenario
- [ ] duplicate publish protections verified
- [ ] raw payload and publication audit trail verified
- [ ] shop modes explicitly reviewed
- [ ] rollback/disable procedure documented

## Ongoing operations
- [ ] health checks reviewed daily
- [ ] sync lag monitored
- [ ] failed publishes reviewed
- [ ] media backlog reviewed
- [ ] prompt/template changes versioned
- [ ] API changes in WB monitored
