# Integration pass 027 — CI-enforced release-readiness contract

The repository's GitHub Actions workflow now runs the machine release-readiness
auditor on every push/refresh and pull-request validation.

## What changed

The progress workflow now requires:

- source-map freshness,
- treemap freshness,
- `tools/release_readiness.py --check`,
- the complete public unit/tooling suite.

This means the tracked machine-ready state can no longer silently drift if a
required evidence file is deleted, source-map counts regress, or the documented
21-class / 313-method contract stops being satisfied.

The automated-validation guide was also refreshed to include the newer machine
checks added after pass 020:

- audio sanity,
- mission stress,
- mission fuzz,
- long-duration mission soak,
- mission-to-mission RMS progression,
- native-image preflight.

This pass adds no new gameplay fidelity claim. It makes the existing objective
finish-line contract continuously enforced by CI.
