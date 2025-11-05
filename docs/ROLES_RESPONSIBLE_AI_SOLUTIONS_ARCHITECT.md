# Responsible AI Solutions Architect

The Responsible AI Solutions Architect designs, plans, and oversees end‑to‑end AI systems with reliability, safety, and compliance built in from day one.

## Core Responsibilities
- Strategy to Implementation Bridge: Translate business objectives into actionable AI architecture and delivery roadmaps.
- Technology Selection: Choose models, providers, data sources, and MLOps platforms that meet cost, performance, and risk constraints.
- Architecture Blueprinting: Produce diagrams and specs for scalable, secure, and observable AI services.
- Risk Mitigation: Ensure feasibility, cost control, security, and compliance (privacy, safety) before build.
- Cross‑Functional Alignment: Coordinate data science, engineering, security, and product stakeholders.

## What This Role Adds Here
- SLOs and Error Budgets: Defines SLIs/SLOs and burn‑rate alerts to quantify reliability of triad failover and DR posture.
- Safety Validation: Provisions Overwatch verification (model‑based) and CI safety gates with golden datasets.
- Cost Guardrails: Tracks token/cost per request and chooses models by domain triads for value.
- Compliance Path: Plans audit logging, e‑signatures, provenance, and validation for regulated phases.

## Operational Objectives (this repo)
1) Enforce SLOs on `/api/chat`:
   - Latency (TTFT & total): 99% < 1.5s; P95 ≤ 2s
   - Error Rate (Overwatch‑pass): 99.9%+ over 7d
   - Availability: 99.99% monthly
2) Burn‑Rate Alerts: 2h/1h multi‑window rules to act before violations.
3) Cost Tracking: Optional token/cost SLI by provider/model.

See also: `docs/SLO_SLI_DEFINITIONS.md`, `monitoring/alert-rules.yaml`, and `monitoring/servicemonitor-backend.yaml`.
