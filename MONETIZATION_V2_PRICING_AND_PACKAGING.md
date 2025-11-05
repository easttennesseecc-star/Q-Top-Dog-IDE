> Archived. See `.archive/outdated_documentation/MONETIZATION_V2_PRICING_AND_PACKAGING.md` and `PRICING_FLAT_SUBSCRIPTIONS.md`.


## Objectives

- Align pricing with current model costs and your exported SLIs (consistency, hallucination severity, TCU budgets).
- Offer clear tiers (Starter, Pro, Enterprise) with measurable value and controllable margins.
- Support usage-based billing on TCU/credits with overage, BYOK discounts, and add-ons (policy packs, provenance/attestation, drift guards).
- Define the metering schema and alerting hooks needed for accurate billing and spend safety.

## Key Concepts

- TCU (Token Compute Unit): normalized compute unit used for usage-based billing. Suggested mapping:
  - TCU ~= (prompt_tokens + completion_tokens) adjusted by model multiplier and tool usage overhead.
  - Include gateway/OPA enforcement, safety prefilter, and verification (KMS) overhead in COGS.
- SLIs → SLAs: Use existing exporters and alerts for tiered commitments.
  - Consistency score ≥ threshold
  - Hallucination severity ≤ threshold
  - Budget adherence: monthly TCU cap with alerts and soft-stop behavior

## Unit Economics (update quarterly)

- Model price table (illustrative — replace with current values):
  - frontier-premium: $X.XX / 1k tokens (multiplier 1.6–2.0)
  - general-purpose: $Y.YY / 1k tokens (multiplier 1.0)
  - small/fast: $Z.ZZ / 1k tokens (multiplier 0.5–0.7)
- Overheads to include in COGS per request:
  - Gateway/OPA policy eval (ms + CPU), Safety prefilter (tokenized check), Verification (KMS sign/verify), Storage/egress for provenance
- Target gross margin by tier:
  - Starter: 60–65%
  - Pro: 70–75%
  - Enterprise: 75–80%+

Formula (per 1k tokens):
- COGS = (model_cost * model_multiplier) + safety_cost + gateway_cost + verification_cost + storage/egress
- Price_per_1k = COGS / (1 - target_margin)

## Plan Tiers (draft)

| Plan | Monthly Price | Included Credits (TCU) | Overage ($/TCU) | SLAs (backed by SLIs) | Features |
|------|----------------|------------------------|------------------|-----------------------|----------|
| Starter | $49 | 50k | $0.0015 | Consistency ≥ 0.70, Hallucination ≤ 0.70 | Basic gateway + safety, community support |
| Pro | $199 | 250k | $0.0012 | Consistency ≥ 0.75, Hallucination ≤ 0.60 | Policy pack A, provenance/attestation, email support |
| Enterprise | Custom (annual) | Committed volume | Custom | Consistency ≥ 0.80, Hallucination ≤ 0.50 | BYOK, data residency, private deploy, custom OPA, SSO, priority routing |

Notes:
- Numbers are placeholders; recompute with the Unit Economics table. Adjust caps/overage to hit target margins.
- Consider geo-based pricing and education/non-profit discounts.

## Add-ons (upsells)

- Advanced Safety Policy Packs (OPA modules)
- Verified Provenance (KMS-backed attestations)
- Drift Guard + Red-Team Automation
- Priority Routing (lower p95 latency SLAs)
- Premium models (frontier access) — per-model surcharge/multiplier

## Medical & Scientific Data Pricing (regulated segments)

Some workloads carry higher compliance and reliability requirements (PHI/PII, HIPAA, clinical/biomedical, regulated scientific data). Price these as segment SKUs with stricter SLAs and added compliance features.

Segment definition and scope:
- medical: Any data containing PHI or subject to HIPAA/HITRUST; e.g., clinical notes, lab results, medical images metadata.
- scientific: High-stakes scientific/technical content requiring citations/provenance and lower hallucination tolerance; e.g., biotech, materials, climate.

Segment multipliers and surcharges (baseline guidance; tune quarterly):
- medical: +20–35% over standard overage rates; BYOK required for Enterprise discount. Frontier model surcharge may apply.
- scientific: +10–20% over standard overage rates.

Included features by segment:
- medical: PHI scrubbing + policy pack, audit logs (immutable), data residency controls, verified provenance (KMS), stricter SLAs.
- scientific: Citation mode, source-link density targets, provenance, stricter hallucination thresholds.

Suggested SLA thresholds (align to Prometheus rules):
- medical: consistency ≥ 0.80; hallucination ≤ 0.45; p95 latency ≤ 2.0s
- scientific: consistency ≥ 0.78; hallucination ≤ 0.55; p95 latency ≤ 2.2s

Packaging options:
- Add-on to core plans (Starter/Pro/Enterprise) with segment surcharge, selected per-project or per-API key.
- Dedicated SKUs ("Pro-Med", "Enterprise-Scientific") with bundled features and audits.

Example pricing (illustrative):
- Pro-Med: $299/mo, 250k TCU; overage $0.0015/TCU (BYOK: $0.0013)
- Pro-Scientific: $239/mo, 250k TCU; overage $0.0014/TCU (BYOK: $0.00125)

Metering additions:
- Add field `data_segment: "general|medical|scientific"` and `verified: true|false`.
- Emit `policy_pack` and `residency` tags when applicable for audit.

UI & selection:
- Allow selecting a data segment at API key or project level. Deny requests that violate policy (OPA) or lack configured protections.

## BYOK vs Platform-Key Pricing

- BYOK discount: -10% to -20% on overage (you avoid some margin leakage and egress)
- Platform key: standard rates with managed secrets, monitoring, and rotation included

## Marketplace Monetization

- Public listings: baseline rev-share X% (set per category)
- Private/enterprise listings: higher rev-share to the publisher; platform fee per-tenant
- Quality gates: listings must meet SLA thresholds (consistency/hallucination), pass safety policy checks, and export required metrics

## Metering Event Schema (required fields)

Emit one metering event per request (and per tool-call if billed):

```json
{
  "tenant_id": "org_123",
  "project_id": "proj_abc",
  "request_id": "uuid",
  "timestamp": "2025-11-02T18:25:43Z",
  "model": "gpt-XYZ",
  "route": "envoy->backend",
  "key_type": "byok|platform",
  "region": "us-east-1",
  "tcu_used": 123.4,
  "tokens_in": 800,
  "tokens_out": 600,
  "model_multiplier": 1.0,
  "latency_ms": 850,
  "cache_hit": false,
  "safety_violations": 0,
  "hallucination_severity": 0.18,
  "consistency_score": 0.82,
  "verified": true,
  "policy_pack": ["baseline", "finance"],
  "status": "ok|denied|error"
}
```

Implementation notes:
- Persist raw events to durable storage; aggregate hourly for billing.
- Include opaque identifiers only; do not store sensitive content in billing streams.

## Billing Logic

- Monthly credit buckets (TCU) per tenant
- Overage billed daily in arrears (or monthly with thresholded alerts)
- Soft-stop at 90% (headers + warning), optional hard-stop at 100% for Starter
- Proration rules for mid-cycle upgrades; credit rollover policy (e.g., up to 20%)

## SLAs backed by Prometheus

Tie plan SLAs to existing rules in `observability/prometheus/alerts.yml`:
- ConsistencyLow — triggers at tier-specific thresholds
- HallucinationHigh — tier-specific thresholds
- TCUExceedsBudget — warns at 80/90/100% usage

Expose per-tenant labels (tenant_id, plan) on exported metrics to support SLA reports.

## Financial Projections & Profit Assurance

This section gives a simple, auditable model for monthly revenue, COGS, and margin, plus safety guardrails you can wire to Prometheus/Grafana. Replace the example numbers with your real unit economics and tenant counts.

### Inputs (variables)

- Tenants per plan: Starter=S_t, Pro=P_t, Enterprise=E_t
- Monthly subscription price: Starter=S_price, Pro=P_price, Enterprise=E_price
- Included TCU per plan: S_inc, P_inc, E_inc
- Average monthly TCU use per tenant (by plan and segment): S_use(seg), P_use(seg), E_use(seg)
- Overage price per TCU (by plan, segment multipliers): overage(plan, seg)
- BYOK discount factor (applied to overage): byok_disc in [0, 0.3]
- Mix: fraction of tenants in each data segment (general/medical/scientific): mix(plan, seg) sums to 1 per plan
- COGS per TCU by segment (includes model cost and overheads): cogs(seg)
- Fixed monthly overhead (support, control-plane, observability): fixed_cost

Recommended segment multipliers (illustrative):
- medical: +20–35% on overage; cogs higher due to compliance
- scientific: +10–20% on overage; cogs slightly higher vs general

### Formulas

For each plan p ∈ {S, P, E} and segment seg ∈ {general, medical, scientific}:

- tenants(p, seg) = total_tenants(p) × mix(p, seg)
- included_tcu(p, seg) = tenants(p, seg) × inc(p)
- used_tcu(p, seg) = tenants(p, seg) × use(p, seg)
- overage_tcu(p, seg) = max(0, used_tcu(p, seg) − included_tcu(p, seg))
- effective_overage_price(p, seg) = overage(p, seg) × (1 − byok_disc)
- subscription_revenue(p) = total_tenants(p) × price(p)
- overage_revenue(p, seg) = overage_tcu(p, seg) × effective_overage_price(p, seg)
- revenue = Σ_p subscription_revenue(p) + Σ_{p,seg} overage_revenue(p, seg)
- cogs = Σ_{p,seg} used_tcu(p, seg) × cogs(seg) + fixed_cost
- gross_margin_pct = (revenue − cogs) / max(revenue, ε)

Notes:
- If Enterprise has committed volume pricing, set price(E) to the MRC and adjust overage accordingly.
- Apply further model-specific surcharges via cogs(seg) and overage(p, seg) multipliers if frontier models are used.

### Example (illustrative only)

| Variable | Value |
|---|---|
| S_t | 800 tenants |
| P_t | 200 tenants |
| E_t | 20 tenants |
| S_price / P_price / E_price | $49 / $199 / $6,000 |
| S_inc / P_inc / E_inc | 50k / 250k / 5M TCU |
| mix S (gen/med/sci) | 0.9 / 0.07 / 0.03 |
| mix P (gen/med/sci) | 0.8 / 0.15 / 0.05 |
| mix E (gen/med/sci) | 0.7 / 0.2 / 0.1 |
| avg use S (gen/med/sci) | 40k / 60k / 55k |
| avg use P (gen/med/sci) | 300k / 380k / 340k |
| avg use E (gen/med/sci) | 6M / 7.5M / 6.8M |
| overage S/P/E (gen) | 0.0015 / 0.0012 / 0.0010 $/TCU |
| segment uplift (med/sci) | +30% / +15% |
| byok_disc | 10% (for BYOK keys) |
| cogs (gen/med/sci) | 0.00035 / 0.00048 / 0.00042 $/TCU |
| fixed_cost | $85,000 |

With these inputs, you can compute overage only where avg use exceeds included caps, then compute revenue, cogs, and margin. Keep margins ≥70% on Pro/Enterprise mixes; adjust prices or caps if margin drifts below target.

### Profit assurance guardrails

Operationalize guardrails so margin drift gets caught early. Ideally, export the following counters from billing aggregation (hourly rollups):

- revenue_usd{plan,segment}
- cost_usd{segment}
- tcu_used_total{plan,segment}

Define helper recording rules (optional):

```
# recording rules (Prometheus)
# margin percentage as a gauge (0..1)
margin_pct = (sum(revenue_usd) - sum(cost_usd)) / clamp_min(sum(revenue_usd), 1)
margin_pct_plan = (sum by (plan) (revenue_usd) - sum by (plan) (cost_usd)) / clamp_min(sum by (plan) (revenue_usd), 1)
```

Alerts (tune thresholds to your targets):

```
groups:
- name: topdog-profit-guardrails
  rules:
  - alert: GrossMarginLow_Global
    expr: margin_pct < 0.68
    for: 30m
    labels: { severity: critical }
    annotations:
      summary: "Gross margin below 68%"
      description: "Global gross margin {{ $value | humanizePercentage }} < 68% for 30m"

  - alert: GrossMarginLow_Pro
    expr: margin_pct_plan{plan="Pro"} < 0.72
    for: 30m
    labels: { severity: warning }
    annotations:
      summary: "Pro margin below 72%"

  - alert: MarginDriftDown_7d
    expr: avg_over_time(margin_pct[7d]) < (avg_over_time(margin_pct[14d]) - 0.05)
    for: 1h
    labels: { severity: warning }
    annotations:
      summary: "Margin dropped >5pp vs prior 14d average"
```

If you’re not ready to export revenue/cost counters into Prometheus, mirror the same guardrails in your billing warehouse (e.g., scheduled checks) and send incidents to Ops.

### Scenario planning (quick worksheet)

Maintain a small CSV or sheet with the inputs above. Minimum tabs:
- Inputs (tenants by plan/segment, prices, caps, cogs, uplifts, BYOK discount, fixed_cost)
- Calc (subscription_revenue, overage, total revenue, cogs, margin by plan and global)
- Scenarios (Conservative / Base / Optimistic) with levers:
  - Tenant growth ±X%
  - Mix shift toward regulated segments ±Ypp
  - Model mix shift to frontier (cogs up) ±Z%
  - BYOK adoption rate ±Wpp

Success criteria: gross_margin_pct ≥ target across Base and within 2–3pp in Conservative; if not, raise overage price or adjust included TCU.

## Rollout & Migration

- Phase 1 (1–2 weeks):
  - Refresh unit economics; finalize plan tables and overage
  - Implement metering fields; validate against Prometheus and billing store
  - Update docs and marketplace terms
- Phase 2 (2–4 weeks):
  - Migrate existing tenants with grandfathered terms; communicate changes and grace periods
  - Enable BYOK discounts and premium model add-ons
  - Add spend alerts and dashboard cards in Grafana

## Repository touchpoints

Update or link these docs after this spec stabilizes:
- `AI_AGENT_MARKETPLACE_SPEC.md` — pricing tables + rev-share
- `AI_AGENT_MARKETPLACE_QUICK_START.md` — plan selection and credit concepts
- `AI_AGENT_MARKETPLACE_INTEGRATION_GUIDE.md` — metering event examples and headers
- `API_KEYS_vs_BYOK_LLM_CLARIFICATION.md` — discount policy
- `CONFIGURATION_REFERENCE.md` — plan caps, overage rates, BYOK flags
- `observability/prometheus/alerts.yml` — thresholds per plan (labels)

## Open Questions

- Final rev-share percentages per category; private listing fees
- Frontier model surcharge table by provider
- Exact TCU normalization formula for tool-augmented calls

---

Appendix A: Example Tier Thresholds (to tune with real data)
- Starter: consistency ≥ 0.70; hallucination ≤ 0.70; p95 latency ≤ 2.5s
- Pro:     consistency ≥ 0.75; hallucination ≤ 0.60; p95 latency ≤ 1.8s
- Enterprise: consistency ≥ 0.80; hallucination ≤ 0.50; p95 latency ≤ 1.2s
