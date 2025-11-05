# Deployment Rollout Plan

This plan describes the staged rollout for the Top Dog API stack with safety prefiltering, KMS-backed verification, consistency/hallucination SLIs, and alert gating.

## Scope
- FastAPI backend, OPA policy (safety.rego), gateway (NGINX → Envoy), Prometheus alerts.
- Feature flags: safety prefilter, adaptive compute budgets, KMS signer, consistency exporter.

## Prereqs
- Secrets/env set via `.env` and mounted in compose.
- Prometheus loaded with rules: `observability/prometheus/alerts.yml` (prometheus.yml includes `rule_files`).
- Canary datasets prepared for `/agent/orchestrate` and consistency SLI.
- Runbooks and dashboards available to on-call.

## Stages
1. Preprod canary (1–5% traffic)
   - Duration: 1–2 hours
   - Gates (must PASS):
     - ConsistencyLow: avg(consistency_score) ≥ threshold (e.g., 0.70)
     - HallucinationHigh: hallucination_severity_avg ≤ threshold (e.g., 0.30)
     - TCUExceedsBudget: token compute usage within budget for p95 requests
   - Actions: watch alerts, verify KMS signing path, validate OPA decisions on sampled traffic.

2. Ramp to 20% (stable)
   - Duration: 24 hours hold
   - Continue monitoring the three alerts and error budget burn (5m/1h windows).
   - Verify snapshot/rollback still functioning under load.

3. Full rollout
   - Progressive increases (50% → 100%), contingent on zero pages and healthy SLIs.

## Rollback
- Trigger: Any alert sustained > 10 minutes or error budget burn rate > 2.0.
- Actions:
  - Flip off new features via env flags: safety prefilter, consistency exporter, adaptive budgets, KMS signer fallback to local.
  - Revert to last known good snapshot (see snapshot runbook).
  - Announce in #ops and create incident ticket.

## Observability
- Dashboards: latency, throughput, consistency_score, hallucination_severity, TCU budget.
- Prometheus rules: ConsistencyLow, HallucinationHigh, TCUExceedsBudget.
- Logs: gateway authz allow/deny with reasons from OPA; verification signer results and error codes.

## KPIs (2-week follow-up)
- Consistency_score mean/median (target ≥ 0.75)
- Hallucination severity mean (target ≤ 0.25)
- Error budget: ≤ 10% burn over 2 weeks
- P95 latency within SLO (service-dependent)
- Cost per 1k requests (TCU proxy) flat or ↓

## Runbooks
- OPA policy update + hot reload
- KMS signer health check and rotation
- Snapshot/rollback procedure
- Canary execution checklist and dashboards

## Notes
- For Prometheus in docker-compose, ensure mounts place `prometheus.yml` and `alerts.yml` in the same directory so `rule_files: [alerts.yml]` resolves.
- If Grafana is present, import dashboards that track the SLIs and alert states.
