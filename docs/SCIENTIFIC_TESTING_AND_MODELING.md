# Theoretical Scientific Testing & Modeling

This document outlines three complementary models to harden reliability and safety:

- Formal verification of reasoning paths (Typed Chain‑of‑Thought)
- Fragility and consistency modeling (N‑variant probes)
- Financial/operational cost‑of‑failure modeling (TCU)

## 1) Formal Verification of Reasoning Paths

- Model: reasoning‑as‑a‑program with a typed Chain‑of‑Thought (T‑CoT).
- Artifact: a structured trace of predicates and inference steps (JSON‑serializable).
- Test: verify the intermediate steps with a prover, independent of final text.

Implementation
- Service: `backend/services/formal_verification.py`
  - Minimal rules: `assume`, `modus_ponens`, `transitivity`
  - API: `FormalVerificationService.verify(trace)` → `VerificationResult`
- Example trace:
  ```json
  {
    "assumptions": ["A", "A->B"],
    "goals": ["B"],
    "steps": [
      {"rule": "assume", "out": "A"},
      {"rule": "assume", "out": "A->B"},
      {"rule": "modus_ponens", "in": ["A", "A->B"], "out": "B"}
    ]
  }
  ```
- For high‑stakes use, swap in a proper solver (Z3/Lean 4) behind the same interface.

## 2) Fragility and Consistency Modeling

- Model: adversarial invariance and consistency thresholds.
- Test: N‑variant probe — small, non‑semantic prompt transformations should not flip conclusions.

Implementation
- Agent: `backend/services/consistency_scoring.py`
  - `generate_probes(prompt, n)` – returns N probe prompts
  - `evaluate(prompt, llm_callable, n)` – returns a `ConsistencyResult` with score and pairwise sims
  - Similarity: token‑set Jaccard (swap with embeddings later if desired)
- SLI: publish a consistency score (0..1) to Prometheus and gate deployments on a minimum threshold (see below).

## 3) Financial and Operational Cost of Failure (TCU)

- Model: every failure mode carries a monetary cost; prioritize remediation by dollars.
- Test: Failure‑Cost Attenuation (FCA) — alert on the weighted sum of failures, not just rates.

Implementation
- Metrics: `backend/metrics.py`
  - `llm_requests_total{outcome, failure_cost_usd}` – counter with bucketed `failure_cost_usd` label (`0, 0.01, 1, 10, 100, 1000`)
  - `tcu_unreliability_cost_usd_total` – counter for Total Cost of Unreliability (no labels)
  - Helper: `record_llm_request(outcome, failure_cost_usd)` buckets and increments TCU
- Hook: `backend/main.py` `/agent/orchestrate` records a request with optional `input_data.failure_cost_usd` (default 0)
- PromQL examples:
  - Burn rate (existing): `sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))`
  - TCU window: `sum(increase(tcu_unreliability_cost_usd_total[15m]))`
  - Consistency SLI: define and export your score as a gauge or summary (e.g., `consistency_score{service="orchestrator"}`)

## Canary/Blue‑Green SLO Gate

Enhancements in `tools/slo_burn_rate_gate.py`:
- Flags:
  - `--threshold` – error burn rate
  - `--tcu-threshold` – max allowed TCU over window
  - `--consistency-threshold` – min required consistency
- Env:
  - `PROM_URL`, `PROM_TOKEN` – Prometheus endpoint/auth
  - `SLO_QUERY` – burn‑rate query (default provided)
  - `COST_TCU_QUERY` – query that returns a single TCU value
  - `CONSISTENCY_SLI_QUERY` – query that returns a consistency value (0..1)

The gate fails if any configured threshold is violated.

## Formal Verification Placement

Introduce `FormalVerificationService` between the LLM and Overwatch Triad. Persist the predicate trace for audits and optionally attach a signed hash to outputs. Start with the lightweight checker here; replace with a production‑grade prover in regulated domains.

## Notes

- Labels as numeric strings are bucketed intentionally to avoid high cardinality.
- For rigorous reasoning verification, integrate Z3/Lean or Datalog engine and store traces as artifacts.
- Consistency scoring is a baseline; production systems often combine embeddings and task‑specific success criteria.
