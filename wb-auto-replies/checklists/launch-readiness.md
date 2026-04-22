# Launch Readiness Checklist

## Before first draft launch
- [ ] DB schema applied in target environment
- [ ] all required shops configured
- [x] WB tokens verified
- [x] archive and active APIs tested manually
- [x] separate archive and active sync states verified
- [ ] draft mode enabled for all shops
- [x] debug/dry-run path verified end-to-end
- [ ] karmic templates filled
- [ ] semantic templates seeded
- [x] GPT provider credentials configured
- [x] prompt and safety rules reviewed
- [x] strict name-safety fallback behavior reviewed
- [ ] health tables updating correctly

## Before first publish launch
- [ ] draft pipeline stable for several runs
- [ ] draft quality manually reviewed
- [x] name safety fallback verified
- [ ] media analysis checked on real examples
- [x] feedback versioning behavior verified
- [x] publish only latest feedback version
- [x] publish client tested in controlled scenario
- [x] duplicate publish protections verified
- [x] raw payload and publication audit trail verified
- [ ] shop modes explicitly reviewed
- [ ] rollback/disable procedure documented

## Ongoing operations
- [ ] health checks reviewed daily
- [ ] sync lag monitored
- [ ] failed publishes reviewed
- [ ] media backlog reviewed
- [ ] prompt/template changes versioned
- [ ] API changes in WB monitored
