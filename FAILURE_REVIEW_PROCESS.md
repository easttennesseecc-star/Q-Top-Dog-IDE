# Failure Review Process

This process standardizes how we detect, triage, mitigate, and learn from failures across TopDog IDE (services, APIs, agents, and CI/CD). It links directly to our snapshot and checkpoint capabilities for safe rollback and clear evidence capture.

## Goals
- Minimize customer impact (fast mitigation/rollback)
- Preserve evidence (snapshots, logs, metrics)
- Produce a concise, high-signal Root Cause Analysis (RCA)
- Drive preventative actions with owners, deadlines, and verification

## When to trigger a Failure Review
Trigger when any of these occur:
- Production incident or degraded SLO (latency, error rate, cost budget, or token burn rate)
- Security/privacy issue or policy violation (e.g., regulated-domain bypass)
- Repeated CI failures or flaky tests impacting delivery
- Snapshot-based rollback required to restore service

## Roles and responsibilities
- Incident Commander (IC): Coordinates response and comms, ensures timelines are met
- Tech Lead (TL): Leads technical mitigation and RCA
- SRE/Platform: Infra and rollback execution; evidence gathering
- QA/RAI (Responsible AI): Evaluates policy/safety regressions; verifies guardrails
- Product/Support: Customer comms, impact assessment

## Severity levels and initial timelines
- Sev 1 (critical, customer-impacting):
  - Mitigation/rollback: within 15 minutes
  - Initial notes: within 1 hour
  - Full RCA: within 48 hours
- Sev 2 (degraded, partial impact):
  - Mitigation/rollback: within 60 minutes
  - Initial notes: within 4 hours
  - Full RCA: within 72 hours
- Sev 3 (internal/CI-only or minor):
  - Mitigation/workaround: within 1 business day
  - RCA: within 5 business days

## Step-by-step process

1) Detection
- Alarms and dashboards: Prometheus/Grafana (SLO burn rate, error rate, latency, token/cost SLIs)
- CI gates: tests, ruff, mypy, golden datasets, Overwatch verification
- Customer reports via support channel

2) Triage and ownership
- Assign IC and TL
- Classify severity (Sev 1–3)
- Open an Incident Issue using our template (see .github/ISSUE_TEMPLATE/incident_report.md)

3) Evidence collection (do not mutate systems yet)
- Snapshots: list and fetch from /snapshots/{workflow_id}
- Checkpoints: list at /snapshots/{workflow_id}/checkpoints
- Logs: app logs, ingress logs, workflow event history
- Metrics and traces: Grafana dashboards, Prometheus scrapes
- Version info: commit, build, feature flags, edition (dev/regulated)

4) Mitigation path
- Prefer safe rollback via snapshot checkpoints
- If no checkpoint applies, use feature flags or canary disable
- If still failing, apply hotfix behind guards

5) Rollback using checkpoints
- Identify latest or named checkpoint for affected workflow_id
- Roll back: POST /snapshots/{workflow_id}/rollback-to-checkpoint with {"label": "<name>"}
- Validate: health checks, error rate, SLOs, and representative flows

6) Root Cause Analysis (RCA)
- Include:
  - Impact timeline and scope
  - Primary cause and contributing factors
  - Why it escaped (tests, gates, reviews)
  - Specific code/config changes involved
  - Evidence links: snapshots, logs, dashboards
- Techniques: 5 Whys; causal chain with guardrail mapping (Overwatch/triad)

7) Actions and verification
- Preventative actions with owners and due dates (lint/type/test expansions; policy-as-code rules; rate limits; circuit breakers)
- Verification plan: tests or golden datasets; Overwatch gates; canary task list
- Close the loop: confirm actions landed and gates enforce the fix

8) Communication
- Internal: incident channel updates at defined cadence until resolved
- External: coordinated customer updates for Sev 1–2
- Final write-up: link to incident issue and RCA doc

## Artifacts to attach to the incident
- Snapshot inventory and the exact file used for rollback (if any)
- Overwatch results (before/after)
- Relevant logs and metrics
- CI run URLs and commit hashes

## Quality gates to check
- Tests: pytest suite
- Type checks: mypy (targeted modules; incrementally expanding)
- Lint: ruff (and policy-as-code rules where applicable)
- Golden datasets evaluation

## Appendix: Snapshot/Checkpoint quick reference
- List all snapshots: GET /snapshots/{workflow_id}
- Fetch latest snapshot: GET /snapshots/{workflow_id}/latest
- Create checkpoint: POST /snapshots/{workflow_id}/checkpoint {"label": "pre-release"}
- List only checkpoints: GET /snapshots/{workflow_id}/checkpoints
- Roll back to named checkpoint: POST /snapshots/{workflow_id}/rollback-to-checkpoint {"label": "pre-release"}
- Labels catalog: GET /snapshots/labels

Notes:
- Snapshot routes can be gated with ENABLE_SNAPSHOT_API and optional auth via REQUIRE_SNAPSHOT_AUTH.
- In test/dev, rollback and checkpoint creation work without a DB (in-memory service mode).

## Post-incident closure checklist
- [ ] Impact confirmed resolved (SLOs steady)
- [ ] RCA approved by IC and TL
- [ ] Actions created with owners and due dates
- [ ] Verification plan merged (tests/gates) and observed green
- [ ] Customer comms (if applicable) sent and archived
- [ ] Learnings added to playbooks/runbooks
