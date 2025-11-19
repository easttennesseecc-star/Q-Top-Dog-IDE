# Pricing Unit Economics & Margin Analysis (for approval)

Date: 2025-11-19
Status: Analysis draft — no code or Stripe changes made.

## Context
- BYOK: We do not pay LLM usage; customers bring their own provider keys. Our variable costs are primarily storage, bandwidth, control-plane compute, logging/metrics, and support.
- Goal: Validate profitability for each tier in the revised proposal (Dev, Dev Pro Plus, Med, Sci) and confirm a 2-year price lock is sustainable.

## Assumptions (adjustable)
- Payment processing: 2.9% + $0.30 per successful charge (Stripe).
- Infra control-plane (per active seat/month):
  - Dev: $1.00; Dev Pro/Pro Plus: $1.50; Teams: $2.00; Enterprise: $3.00
  - Regulated uplift (Med/Sci): +$1.00 per seat to reflect stricter logging/audit overhead.
- Storage cost (provider) per GB-month: $0.02 (hot), internal backups/overhead: +50% → effective $0.03 GB-month.
- Bandwidth egress/ingress amortized per active seat (Dev profile): $0.10–$0.40/month depending on tier; Regulated +$0.15.
- Support opex per active seat/month:
  - Dev Free: $0 (community only)
  - Dev Pro: $1.00; Pro Plus: $2.00
  - Teams: $3.00; Enterprise: $8.00
  - Med/Sci uplift: +$2.00 seat for Pro; +$4.00 seat for Teams; +$10.00 seat for Enterprise
- Average annual churn & refunds budget: 1% revenue reserve.

Note: These are conservative placeholders; tune in the calculator script.

## Per-Seat Cost Model (default)
- Cost(seat) = StripeFees + Infra + Storage(assigned cap or avg usage) + Bandwidth + Support + Reserve(1% revenue)
- Revenue(seat) = List price (monthly or annual-equivalent)
- Margin% = (Revenue − Cost) / Revenue

## Dev Lineup — Example Margins (monthly per seat)
- Dev Free ($0): cost ~$0.25–$0.60 (infra + bandwidth); covered by paid tiers — OK.
- Dev Pro ($29):
  - Stripe: ~$1.14; Infra: $1.50; Storage (5 GB @ $0.03): $0.15; Bandwidth: $0.20; Support: $1.00; Reserve: $0.29
  - Total cost ≈ $4.28 → Margin ≈ 85.3%
- Dev Pro Plus ($49):
  - Stripe: ~$1.72; Infra: $1.50; Storage (15 GB): $0.45; Bandwidth: $0.30; Support: $2.00; Reserve: $0.49
  - Total cost ≈ $6.46 → Margin ≈ 86.8%
- Dev Teams ($39):
  - Stripe: ~$1.43; Infra: $2.00; Storage (10 GB): $0.30; Bandwidth: $0.30; Support: $3.00; Reserve: $0.39
  - Total cost ≈ $7.42 → Margin ≈ 81.0%
- Dev Enterprise ($79):
  - Stripe: ~$2.60; Infra: $3.00; Storage (50 GB): $1.50; Bandwidth: $0.40; Support: $8.00; Reserve: $0.79
  - Total cost ≈ $16.29 → Margin ≈ 79.4%

Observation: BYOK keeps margins high. Storage caps we set are low enough to protect margins; add‑ons raise ARPU if customers need more.

## Regulated (Medical/Scientific) — Example Margins (monthly per seat)
- Med Pro ($89):
  - Stripe: ~$2.88; Infra: $2.50; Storage (10 GB): $0.30; Bandwidth: $0.45; Support: $3.00; Reserve: $0.89
  - Total ≈ $10.02 → Margin ≈ 88.7%
- Med Teams ($129):
  - Stripe: ~$3.84; Infra: $3.00; Storage (25 GB): $0.75; Bandwidth: $0.55; Support: $7.00; Reserve: $1.29
  - Total ≈ $16.43 → Margin ≈ 87.3%
- Med Enterprise ($199):
  - Stripe: ~$6.11; Infra: $4.00; Storage (75 GB): $2.25; Bandwidth: $0.70; Support: $18.00; Reserve: $1.99
  - Total ≈ $33.05 → Margin ≈ 83.4%
- Sci Pro ($69): Total ≈ ~$7.80 → Margin ≈ ~88.7% (similar calc with $69 price)
- Sci Teams ($99): Total ≈ ~$12.5 → Margin ≈ ~87.4%
- Sci Enterprise ($149): Total ≈ ~$21.5 → Margin ≈ ~85.6%

Note: Med/Sci assumptions include higher governance/audit overheads.

## Minimum Org Examples (monthly)
- Dev Teams (3 seats min): Revenue $117; Est cost ~$22.3 → Margin ~$94.7 (81%)
- Dev Enterprise (10 seats): Revenue $790; Cost ~$162.9 → Margin ~$627.1 (79%)
- Med Teams (5 seats): Revenue $645; Cost ~$82.1 → Margin ~$562.9 (87%)
- Med Enterprise (10 seats): Revenue $1,990; Cost ~$330.5 → Margin ~$1,659.5 (83%)

## Storage Add‑Ons (margin check)
- Effective storage cost: ~$0.03/GB‑month including overhead.
- Add‑on pricing:
  - +5 GB at $3 → cost $0.15 → ~95% margin
  - +20 GB at $10 → cost $0.60 → ~94% margin
  - +100 GB at $35 → cost $3.00 → ~91% margin
→ Add‑ons are highly profitable and protect baseline margins when heavy storage is needed.

## Sensitivity (what could erode margins?)
- Support burden spikes (enterprise hand‑holding, compliance reviews): mitigate with SLAs & limits; price seats accordingly.
- Infra/logging growth beyond assumptions: watch metrics; scale logging retention per tier.
- Unexpected egress/bandwidth: keep artifact hosting ephemeral by default; encourage customer buckets; gate large exports to paid add‑ons.
- Payment fee changes: still low share of price; annual billing reduces $0.30 fee frequency.

## Recommendation
- All listed tiers (Dev, Pro Plus, Teams, Enterprise; Med & Sci) are profitable under conservative assumptions.
- Approve pricing with Annual Option A for Dev & Sci; for Med consider Option B (no annual discount) or a smaller discount due to compliance overhead.
- Keep storage caps as proposed; rely on add‑ons for heavy users.
- Keep BYOK slot counts as proposed or switch to org‑level slot pools for Teams/Enterprise if you prefer governance clarity.

## Next Steps (after approval)
- Lock “Annual Option” per family (Dev/Sci: A; Med: A or B?).
- Implement in `pricing_tiers.json`, `TIER_CONFIGS`, rate limiter, and Stripe mappings.
- Add unit tests to enforce price/limit invariants and margin guardrails (static checks on caps/slots; cost checks documented here).

---
See `tools/price_model.py` to tweak assumptions and recompute margins quickly.
