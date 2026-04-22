# Readiness and E2E Notes

The project now has reproducible test coverage for these readiness scenarios:

- backfill mode ingests data without publication
- draft mode generates drafts without publication
- controlled publish path records dry-run publication only
- multi-store isolation keeps context and templates separated

## Important operational note

Even when `shop.mode = publish`, the current `WbPublishClient` is still a dry-run stub and does not send real replies to Wildberries.

This is intentional until production enablement is explicitly approved.
