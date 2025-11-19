# Top Dog IDE — Dev Tier & Pricing Proposal (Revised Premium Positioning)

Date: 2025-11-19 (Revision 2)
Status: Awaiting approval — no code, database, or Stripe changes applied.

## Revision Notes
You asked that pricing reflect a secure, auditable, multi‑LLM orchestration platform (not just an IDE) while staying accessible to hobbyists and beginners. This revision:
1. Elevates perceived value (multi‑LLM orchestration, audit trails, formal verification, consistency scoring, provenance, security guardrails, SLO reliability).
2. Keeps an approachable Free tier and a clear solo on‑ramp.
3. Maintains monotonic feature/limit growth and sensible per‑seat economics.

## Objectives (unchanged intent, reprioritized)
1. Premium differentiation: Emphasize orchestration, compliance readiness, provenance & verification features.
2. Accessibility: Preserve a robust Free tier; offer an affordable Solo (Pro) path.
3. Clear progression: Free → Pro (Solo depth) → Teams (collaboration & governance) → Enterprise (scaled coordination & advanced auditing).
4. Implementation safety: All changes gated by your explicit approval; Stripe & DB untouched for now.

## Proposed Pricing (USD)
| Tier | Audience | Monthly (per seat) | Annual (per seat equiv) | Min Seats | Positioning |
|------|----------|-------------------:|------------------------:|----------:|-------------|
| Dev Free | Hobbyist / Evaluation | $0 | $0 | 1 | Explore multi‑LLM basics, community only |
| Dev Pro | Serious Solo Builder | $29 | $26.10 (10% discount) | 1 | Full orchestration depth, personal audit trail |
| Dev Pro Plus | Power Solo — Full Dev Surface | $49 | $44.10 (10% discount) | 1 | Unlocks the full developer feature set for one user |
| Dev Teams | Collaborative Product Teams | $39 | $35.10 (10% discount) | 3 | Shared workspaces, pooled quotas, governance light |
| Dev Enterprise | Scale & Governance | $79 | $71.10 (10% discount) | 10 | Advanced RBAC, deep audits, policy + attestation |

Rationale:
- Distinct jump at each tier reflects added coordination & compliance value.
- Annual discount set to 10% for Dev tiers (paid upfront) — generous but sustainable.
- Pro stays accessible while signaling “serious” value: multi‑LLM orchestration + verification.
- Pro Plus exists for the one‑person founder who needs everything but team collaboration.
- Teams adds collaboration + pooled usage; Enterprise layers advanced governance & provenance strength.

## Limits & Features (per seat unless noted)

Legend: Daily caps reset at 00:00 UTC. Models: No restrictions — all 53+ LLM options are available at every tier. Teams/Enterprise use organization-level pooled buckets and credential pools where noted.

- Dev Free
  - Daily API calls: 75
  - Daily LLM requests: 40
  - Concurrent sessions: 1
  - Storage: 500 MB
  - Agent roles: up to 2 roles (Assistant, Tester)
  - Support: Community forum
  - Multi‑LLM: Basic BYOK (no keys provided); marketplace browse, limited runs
  - Verification: Consistency scoring (read-only), no formal verification export
  - Provenance: Basic snapshot history (7-day retention)
  - API key slots (BYOK): 2
  - Production gating (taste power, not production-ready):
    - Limited throughput and concurrency; batch & automation disabled
    - No project export beyond small bundles; repo cap ~100 MB
    - Watermarked/non-attested outputs; no custom webhooks or CI integrations
    - Ephemeral artifacts; no long-term artifact hosting

- Dev Pro
  - Daily API calls: 800
  - Daily LLM requests: 300
  - Concurrent sessions: 2
  - Storage: 5 GB
  - Agent roles: up to 3 roles (Assistant, Builder, Tester)
  - Support: Standard (email, ≤48h target)
  - Multi‑LLM: Full orchestration; role assignments; local + cloud hybrid
  - Verification: Formal verification endpoint access (limited throughput)
  - Provenance: Extended snapshot retention (30 days), artifact hashes
  - Guardrails: Safety prefilter + hallucination severity export
  - API key slots (BYOK): 3

- Dev Pro Plus
  - Daily API calls: 1,200
  - Daily LLM requests: 450
  - Concurrent sessions: 3
  - Storage: 15 GB
  - Agent roles: up to 5 roles (Assistant, Builder, Tester, Security, Health)
  - Support: Priority-lite (≤36h target)
  - Multi‑LLM: Advanced orchestration policies (personal), role matrices, failover tuning
  - Verification: Increased throughput; batch verification (personal scope)
  - Provenance: 60-day snapshot retention; artifact manifest diffing; hashes
  - Guardrails: Full safety prefilter + hallucination severity export
  - Integrations: Personal CI hooks + inbound webhooks (personal scope)
  - API key slots (BYOK): 5
  - Notes: No shared workspaces, no org RBAC (reserved for Teams/Enterprise)

- Dev Teams (≥3 seats)
  - Daily API calls: 1,600 per seat
  - Org pooled API calls bucket: 400 per seat (shared)
    Example: 6 seats → 9,600 personal + 2,400 org pooled = 12,000 total
  - Daily LLM requests: 600 per seat
  - Concurrent sessions: 3 per seat
  - Storage: 10 GB per seat (org soft cap)
  - Agent roles: all five core roles (Assistant, Builder, Tester, Security, Health)
  - Support: Priority (≤24h target)
  - Multi‑LLM: Shared orchestration policies, team role matrix
  - Verification: Batch formal verification (moderate throughput)
  - Provenance: Audit summaries + artifact manifest diffing
  - Governance: Basic RBAC + workspace sharing
  - Organization BYOK credential pool: 12 base + 2 per seat (shared by org)

- Dev Enterprise (≥10 seats)
  - Daily API calls: 3,500 per seat
  - Org pooled API calls bucket: 1,750 per seat (shared)
  - Daily LLM requests: 1,400 per seat
  - Concurrent sessions: 6 per seat
  - Storage: 50 GB per seat (org hard cap tiers)
  - Agent roles: all five core roles (Assistant, Builder, Tester, Security, Health)
  - Support: Priority+ (business hours SLA) + named account manager
  - Multi‑LLM: Advanced orchestration policies, failover tuning, quota shaping
  - Verification: High-throughput formal verification & attestation signatures
  - Provenance: Deep audit logs (long-term), SBOM embedding, dataset lineage
  - Governance: Full RBAC, policy enforcement hooks, data residency options (dev profile scope)
  - Organization BYOK credential pool: 24 base + 3 per seat (shared by org)
  - Integrations: Custom inbound webhooks, SSO/SAML lite, custom rate shaping

Notes:
- Regulated compliance (HIPAA/SOC2/PHI) remains a future parallel lineup (not modified here).
- Pooled boosts are applied after per-seat caps (i.e., additive shared bucket, not multiplicative per request).
- Monotonic growth preserved; concurrency and verification depth always increase tier to tier.

#### BYOK Credential Slots: Definition, Pools & Failover
- What a slot is: a saved credential for one provider/model account (e.g., OpenAI, Anthropic, Gemini, Ollama endpoint, region variant, or separate quota account). Slots are not “roles”.
- Why more than roles: the orchestrator maintains a candidate pool per role (e.g., coding, analysis, testing, assistant, local). Multiple slots per role enable redundancy (multi‑vendor), region choice, quota split, and blue‑green rotation without retyping keys.
- Auto‑failover: orchestrator health‑checks configured slots and automatically swaps to a healthy slot when a model/provider is down or rate‑limited. No manual switching needed once slots are configured.
- Productivity: higher‑tier users benefit from more pre‑configured backup providers/models, minimizing downtime and allowing specialty models for certain tasks.
- Governance: slots are subject to policy (allowed providers/models) and data‑segment routing. Teams/Enterprise now use organization‑level pools.
- Organization pools (Dev tiers):
  - Teams: 12 base org slots + 2 per seat (shared pool)
  - Enterprise: 24 base org slots + 3 per seat (shared pool)
  - Free/Pro/Pro Plus remain per‑seat: 2 / 3 / 5 slots respectively

### Overwatch (Planner) — Role vs Feature Clarification
- Intent: Overwatch maintains the build plan, detects drift, and requests approval before deviations. It supervises rather than performs domain work.
- Option A — Feature Overlay (recommended): Overwatch is a system feature that wraps existing roles, does not consume a role slot, and is available on all tiers that include any planning capability. Controls live in policy/settings; logs feed into provenance/audit.
- Option B — Dedicated Role (“Planner”): Overwatch counts as a sixth role. On tiers with role limits, enabling Planner consumes one role slot. This reduces available domain roles on Free/Pro.
- Recommendation: Adopt Option A to avoid penalizing smaller tiers; treat Overwatch as a supervisory feature with toggleable strictness. If you prefer Option B, specify which tiers should count Planner toward the role limit.

#### Overwatch Enforcement Model (No‑Babysitting)
- Plan Ledger: Immutable plan graph (`plan_id`, `step_id`, scope, constraints, success criteria). Every action must reference plan/step IDs.
- Action Envelope: All tool calls/edits carry `{plan_id, step_id, intent, targets, diff_preview, budget}` for contextual gating.
- Gatekeeper (Pre‑exec): Deterministic checks enforce scope, dependencies, budget, schema/contracts, and egress whitelists before execution.
- Auto‑remediation: On block, perform bounded deterministic fixes (format/schema/test/grounding fetch/reroute) up to K attempts without interrupting the user.
- Escalation: Request user approval only when auto‑remediation cannot resolve policy conflicts, the change is destructive/irreversible, output is ungroundable after K attempts, or intent is ambiguous.
- Provenance: Log decisions, rules fired, diffs, and remediation attempts to the audit trail.

Hallucination Prevention (Feature)
- Grounding‑first: Factual steps require attached sources (RAG/spec/code/dataset) or are blocked.
- Constrained decoding: Function‑calling/JSON‑schema outputs with strict validators; reject non‑conforming tokens.
- Coverage thresholds: Enforce citation/source coverage ≥T%; otherwise auto‑retrieve and retry; persistently failing → block or escalate.
- Deterministic validators: AST/semantic diff guards, tests/type checks, OpenAPI/spec conformance.
- Sandbox: Per‑step whitelisted files/tools/APIs; all others denied at the gate.

### Storage Add‑Ons (proposed)
- Add 5 GB: +$3/seat/month
- Add 20 GB: +$10/seat/month
- Add 100 GB: +$35/seat/month
Notes: Add‑ons apply to Pro/Teams/Enterprise. Free has no paid storage add‑on; upgrade path only.

## Stripe Plan Mapping (proposed — aligned to final discount policy)

Environment variables will point to Stripe Price IDs. We will provision these in Stripe and update code after your approval.

- `STRIPE_PRICE_ID_PRO` → Dev Pro monthly ($29)
- `STRIPE_PRICE_ID_PRO_ANNUAL` → Dev Pro annual ($26.10 per month billed annually, save 10%)
- `STRIPE_PRICE_ID_PRO_PLUS` → Dev Pro Plus monthly ($49)
- `STRIPE_PRICE_ID_PRO_PLUS_ANNUAL` → Dev Pro Plus annual ($44.10 per month billed annually, save 10%)
- `STRIPE_PRICE_ID_TEAMS` → Dev Teams monthly ($39 seat)
- `STRIPE_PRICE_ID_TEAMS_ANNUAL` → Dev Teams annual ($35.10 per seat per month billed annually, save 10%)
- `STRIPE_PRICE_ID_ENTERPRISE` → Dev Enterprise monthly ($79 seat)
- `STRIPE_PRICE_ID_ENTERPRISE_ANNUAL` → Dev Enterprise annual ($71.10 per seat per month billed annually, save 10%)

Notes:
- Dev tiers have a fixed 10% annual discount applied (paid upfront). Display copy: “$X/mo billed annually (save 10%).”
- Regulated tiers (Medical/Scientific) have no annual discount; annual equals monthly on a per‑month equivalent basis. Implementation can reuse monthly prices or create separate annual prices at the same effective rate.

Storage add‑ons map to separate Stripe prices (metered or flat per seat). We’ll propose concrete IDs after your selection of add‑on sizes.

Code note: current `backend/services/stripe_service.py` exposes `PRICE_IDS = {"pro", "teams"}`. After approval we will add `enterprise` and annual IDs. The `SubscriptionTier` enum already has `FREE/PRO/TEAMS/ENTERPRISE`, which aligns with these names (we will present “Dev …” only at the UI layer to avoid churn). We will also add the `dev_pro_plus` SKU.

## API & Data Model Alignment

Files impacted post-approval:
- `backend/config/pricing_tiers.json` (canonical list surfaced by `/api/tiers`)
- `backend/database/tier_schema.py` (`TIER_CONFIGS` and defaults for `membership_tiers`)
- `backend/services/stripe_service.py` (add Enterprise/annual price IDs; wire through checkout/portal)
- `backend/services/rate_limiter.py` (limits should match the proposal; pooled logic for Teams/Enterprise)
- `backend/routes/pricing_routes.py` (ensure naming surface is “Dev …”; keep `SubscriptionTier` stable)
  - Add new SKU “dev_pro_plus” with limits above Pro, below Teams on collaboration features

Endpoints (read-only):
- `/api/tiers` → marketing/pricing surface (JSON)
- `/api/tier/info` → maps legacy subscription to suggested Dev tier (auth)
- `/api/tier/limits` → returns caps/usage for current user (auth)

## Rollout Plan (post-approval — unchanged sequence)
1) Stripe
   - Create/update price objects: Pro, Pro Annual, Teams, Teams Annual, Dev Enterprise, Dev Enterprise Annual.
   - Record IDs; set env in CI/CD secrets: `STRIPE_PRICE_ID_*`.
2) Backend
   - Update `PRICE_IDS` and optional annual handling in `stripe_service.py`.
   - Update `pricing_tiers.json` + `TIER_CONFIGS` to match limits/prices here.
   - Add pooled usage boost in Teams/Enterprise (25%/50%).
   - Add tests to assert monotonic limits and pricing non-regression.
3) Frontend
   - Ensure pricing cards reflect “Dev …” labels and new copy.
   - Clarify annual savings and per-seat rules; enforce seat minimums in UI.
4) Migration/Safety
   - Existing subscribers: honor grandfathered price until term end; display banner with upgrade path.
   - Smoke test `/api/tiers`, checkout links, and billing portal.

## Open Questions
1. Keep Enterprise at $79 seat or introduce higher “Regulated Enterprise” separately later?
2. Fixed buckets: approve the proposed org pooled API call buckets — Teams: 400 per seat/day; Enterprise: 1,750 per seat/day. If you prefer different sizes or base + per‑seat, specify.
3. BYOK org pools: approve Teams (12 base + 2/seat) and Enterprise (24 base + 3/seat); or provide alternative targets.
4. Any desire for an intermediate “Starter” paid tier (e.g., $12) or is Free + Pro enough?
5. Overwatch: confirm Option A (feature overlay, no role slot) vs Option B (dedicated role that consumes a slot on limited tiers).

---

If you approve this revision, I will implement precisely as stated and supply a migration + regression test summary before activating Stripe changes.

## Regulated Lineup — Medical & Scientific (New)

Purpose: Include regulated profiles for Medical (HIPAA‑readiness and PHI posture) and Scientific (research data governance) with premium pricing, guardrails, and provenance/audit depth beyond Dev.

### Regulated Pricing (USD)
| Tier | Audience | Monthly (per seat) | Annual (per seat equiv) | Min Seats | Positioning |
|------|----------|-------------------:|------------------------:|----------:|-------------|
| Med Pro | Individual in regulated workflows | $89 | $89 (no discount) | 1 | HIPAA‑ready posture, PHI guardrails, audit trail |
| Med Teams | Clinical/ops teams | $129 | $129 (no discount) | 5 | Team governance, RBAC, data residency options |
| Med Enterprise | Scale + compliance leadership | $199 | $199 (no discount) | 10 | Deep audits, BAA option, advanced policy & attestation |
| Sci Pro | Individual researcher/engineer | $69 | $69 (no discount) | 1 | Data governance, provenance, verification |
| Sci Teams | Research groups | $99 | $99 (no discount) | 3 | Shared workspaces, pooled quotas, RBAC light |
| Sci Enterprise | Lab/platform at scale | $149 | $149 (no discount) | 10 | Deep provenance, policy hooks, residency options |

Notes:
- No annual discounts for Medical or Scientific tiers; they pay full price for superior regulated tech.
- No separate “Free” regulated tiers; Dev Free is the evaluation path. Regulated trials can be time‑boxed via coupons if desired.

### Regulated Limits & Features (per seat unless noted)
- Med Pro
  - Daily API calls: 1,200; LLM requests: 450; Concurrent sessions: 3
  - Storage: 10 GB
  - BYOK: API key slots: 5
  - Guardrails: PHI filters, stricter prompt auditing, safety prefilter
  - Verification: Formal verification + attestation export (personal scope)
  - Provenance: 90‑day retention, artifact hashing & SBOM embedding
  - Compliance: HIPAA‑ready posture, audit trail; BAA not included

- Med Teams (≥5 seats)
  - Daily API calls: 2,000 per seat (+ pooled 35% org boost)
  - LLM requests: 800 per seat; Concurrent sessions: 4 per seat
  - Storage: 25 GB per seat (org soft cap)
  - BYOK: API key slots: 7 per seat
  - Governance: RBAC, policy enforcement hooks, data residency options
  - Provenance: Long‑form audit summaries, artifact manifest diffing
  - Compliance: HIPAA‑readiness; optional BAA upgrade path (Enterprise)

- Med Enterprise (≥10 seats)
  - Daily API calls: 4,000 per seat (+ pooled 60% org boost)
  - LLM requests: 1,800 per seat; Concurrent sessions: 8 per seat
  - Storage: 75 GB per seat (org hard cap tiers)
  - BYOK: API key slots: 12 per seat
  - Governance: Full RBAC, policy libraries, advanced residency controls
  - Compliance: BAA option, deep audits, incident logging integration
  - Verification: High‑throughput verification + signed attestations

- Sci Pro
  - Daily API calls: 1,000; LLM requests: 400; Concurrent sessions: 3
  - Storage: 8 GB; BYOK slots: 5
  - Provenance: Dataset lineage tracking; artifact hashing
  - Verification: Batch verification (personal scope)
  - Governance: Light policy hooks

- Sci Teams (≥3 seats)
  - Daily API calls: 1,800 per seat (+ pooled 30% org boost)
  - LLM requests: 700 per seat; Concurrent sessions: 4 per seat
  - Storage: 20 GB per seat (org soft cap); BYOK slots: 7 per seat
  - Provenance: Lab‑style audit summaries; manifest diffing
  - Governance: RBAC light; residency options (selected regions)

- Sci Enterprise (≥10 seats)
  - Daily API calls: 3,800 per seat (+ pooled 55% org boost)
  - LLM requests: 1,500 per seat; Concurrent sessions: 7 per seat
  - Storage: 60 GB per seat (org hard cap tiers); BYOK slots: 12 per seat
  - Provenance: Deep lineage + SBOM; long retention
  - Governance: Full RBAC; policy enforcement; advanced residency

Storage Add‑Ons: Same structure as Dev (5/20/100 GB at $3/$10/$35 per seat/month) for Sci/Med. Storage is controlled to protect margins; heavier archives should move to customer buckets.

### Stripe Mapping (regulated)
- Medical:
  - `STRIPE_PRICE_ID_MED_PRO`, `_ANNUAL`
  - `STRIPE_PRICE_ID_MED_TEAMS`, `_ANNUAL`
  - `STRIPE_PRICE_ID_MED_ENTERPRISE`, `_ANNUAL`
- Scientific:
  - `STRIPE_PRICE_ID_SCI_PRO`, `_ANNUAL`
  - `STRIPE_PRICE_ID_SCI_TEAMS`, `_ANNUAL`
  - `STRIPE_PRICE_ID_SCI_ENTERPRISE`, `_ANNUAL`

Implementation: These map to a “regulated” edition flag already present in the backend. UI surfaces can segment Dev vs Med vs Sci per domain/config.
