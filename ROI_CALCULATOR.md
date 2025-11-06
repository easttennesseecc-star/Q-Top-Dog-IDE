# ROI Calculator: Top Dog Teams vs Copilot + Codespaces

This lightweight calculator helps estimate total cost per seat and per team per year.

- Top Dog Teams: flat $25/seat/month
- Copilot + Codespaces: Copilot monthly + Codespaces hourly compute

Use the PowerShell script in `scripts/roi_calculator.ps1` or the tables below.

---

## Quick Comparison (Defaults)

Assumptions:
- Team size: 5 seats
- Copilot: $10/month per user
- Codespaces: 4‑core machine at $0.36/hour
- Active dev time: 100 hours/month per user

Results:
- Top Dog Teams: $25 × 5 × 12 = $1,500/year
- Copilot + Codespaces: ($10 + $0.36×100) × 5 × 12 = ($10 + $36) × 5 × 12 = $46 × 5 × 12 = $2,760/year per seat → $13,800/year for 5 seats

Savings with Top Dog: ~$12,300/year per 5‑person team (≈90%)

---

## Use the Script (Windows PowerShell)

Run locally from the repo root:

```powershell
# Example: 5 seats, 100 hrs/mo on 4-core, Copilot $10
./scripts/roi_calculator.ps1 -Seats 5 -HoursPerMonth 100 -CoreSize 4 -CopilotMonthly 10

# Try a lower compute scenario: 60 hrs/mo on 2-core
./scripts/roi_calculator.ps1 -Seats 5 -HoursPerMonth 60 -CoreSize 2 -CopilotMonthly 10

# Override Top Dog Teams price (if promotional)
./scripts/roi_calculator.ps1 -Seats 12 -HoursPerMonth 80 -CoreSize 4 -CopilotMonthly 10 -TopDogSeatMonthly 25
```

Outputs per-seat and per-team, monthly and yearly totals.

---

## Rates Reference

- Codespaces (illustrative):
  - 2‑core: $0.18/hour
  - 4‑core: $0.36/hour
  - 8‑core: $0.72/hour
- Copilot (illustrative): $10/month (individual)
- Top Dog Teams: $25/seat/month

Adjust these inputs in the script to match your scenario.

---

## Linkouts

- Executive synthesis: `PRODUCT_AND_MARKET_ANALYSIS.md`
- Pricing and tiers: `Q-IDE_MEMBERSHIP_TIERS_PRICING.md`
- Competitive analysis: `COMPETITIVE_ANALYSIS_Q-IDE_VS_COMPETITION.md`
