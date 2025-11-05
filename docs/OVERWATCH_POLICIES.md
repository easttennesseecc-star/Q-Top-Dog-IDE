# Overwatch Policies by Edition

Overwatch is always available. In Dev Edition it's guidance-first for hallucination prevention; in Regulated Edition it's stricter, can block responses, and adds compliance.

## Dev Edition (software/game dev)
- Required by default (REQUIRE_OVERWATCH_DEV=true)
- Non-blocking by default (BLOCK_ON_OVERWATCH_FAIL_DEV=false)
- Default model: DEFAULT_OVERWATCH_LLM_DEV (e.g., gpt-4o-mini)
- Focus areas:
  1. Factual accuracy (no made-up APIs/paths)
  2. Code/config validity (compiles, correct imports, versions)
  3. References when making strong claims
- Output: JSON { ok, issues[{type,summary,severity}], suggestions }

## Regulated Edition (medical/science)
- Required by default (REQUIRE_OVERWATCH=true)
- Blocking allowed (BLOCK_ON_OVERWATCH_FAIL=true)
- Uses domain triads (MED_/SCIENCE_*) or DEFAULT_OVERWATCH_LLM
- Focus areas:
  1. Factual errors/hallucinations
  2. Unsafe medical/scientific claims
  3. Missing citations
  4. PHI leakage
  5. Regulatory tone and disclaimers
- Output: JSON { ok, issues[{type,summary,severity}], suggestions }

## Metrics
- `overwatch_flagged_total` increments for both editions when ok=false
- Pair with budget/cost and SLO dashboards for operational visibility
