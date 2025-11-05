---
name: "Incident report"
about: "Capture production or pre-prod incident details and RCA"
labels: ["incident", "triage"]
assignees: []
---

## Summary
- Date/time detected:
- Reported by (alarm/support/CI):
- Severity (Sev 1/2/3):
- Affected components:

## Impact
- Customer impact/scope:
- SLOs affected (latency/error/cost):
- Duration:

## Timeline
- T0 detection:
- T+15m mitigation/rollback:
- T+1h initial notes:
- T+48-72h final RCA:

## Evidence
- Snapshots: links to /snapshots/{workflow_id} and file names used
- Logs: links or attachments
- Metrics/dashboards: Grafana panels/screenshots
- CI runs/commits:
- Feature flags/editions active:

## Mitigation and rollback
- What was done (rollback / canary / feature flag / hotfix):
- Validation evidence after mitigation:

## Root Cause Analysis (RCA)
- Primary cause:
- Contributing factors:
- Why it escaped tests/gates:
- Specific change(s) involved (PRs/commits):

## Actions (preventative + validation)
- [ ] Action 1 — owner — due date
- [ ] Action 2 — owner — due date
- [ ] Add/expand tests, golden datasets, or Overwatch rules
- [ ] Confirm gates enforced (mypy/ruff/tests/Overwatch) in CI

## Communication
- Internal updates:
- Customer updates (if applicable):

## Closure
- [ ] Impact resolved and SLOs stable
- [ ] Actions created and tracked
- [ ] Verification plan in place and observed green
- [ ] Learnings documented
