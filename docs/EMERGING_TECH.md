# Emerging Tech Roadmap for Software & Game Dev

This roadmap captures forward-looking capabilities with pragmatic scaffolds in this repo.

## Verified Reasoning & Zero-Knowledge Attestations
- Code: `backend/services/formal_verification.py`, `backend/services/attestation.py`, `/verification/check` endpoint
- What it does: verifies a reasoning trace, computes a proof hash of invariants, signs an attestation. Swap in real ZK later.

## Deterministic AI State for Esports Fairness
- Code: `backend/services/determinism.py`, `/determinism/seed`
- What it does: derives a cryptographic seed/commitment from inputs for adjudication and anti-cheat.

## Compute-Aware AI Budgets (Dynamic LOD for Intelligence)
- Code: `backend/services/ai_budget.py`
- What it does: provide a runtime budget to adapt tokens/tools/time; integrate in orchestration.

## Neuro-Symbolic NPCs with Formal Sandboxing
- Pattern: couple learned policy with symbolic rules checked via `FormalVerificationService` or an external solver; snapshot moves.

## PQC-Ready Economies and Mod Ecosystems
- Policy: `policies/overwatch/attestation.rego` enforces release attestation. Swap Ed25519 -> PQC signatures when ready.

## Privacy Budgets for Telemetry
- DP toggle exists in `SnapshotStore`; extend with per-account budgets and on-device aggregation hooks.

## Generative PCG with Guardrails
- Tool: `tools/pcg_guardrails.py` checks simple asset constraints; extend with solvability checks.

## Latency-Aware AI Copilots in Editors
- Combine compute budgets and consistency/quality SLIs to scale reasoning depth; background long chains.

## Live Safety Canaries in Production
- Consistency SLI: `consistency_score` gauge; `/consistency/sli` endpoints. Gate in canary workflow.

## Autonomous FinOps for Live Ops Events
- Costs: `llm_requests_total{failure_cost_usd}` and `tcu_unreliability_cost_usd_total` link to canary via `--tcu-threshold`.

## Compliance-as-Code & Automated Healing
- Policy: `policies/overwatch/compliance.rego`. Integrate into Overwatch gate.
- Healing: extend CI to generate a Resolution section from failures (starter: `tools/parse_junit.py`).

## Multi-Repo Context & Auto Architecture Modeling
- Starter: `tools/arch_modeler.py` (to be added) could emit PlantUML from file graph. Multi-repo aggregation next.

## Model Drift Auto-Retrain
- Tool: `tools/model_validation_daemon.py` watches consistency_score and triggers retrain webhook on sustained drop.

## Prompt Injection & Agent Hijacking Defense
- Red teaming: `tools/red_team_runner.py`
- Sandboxing: route through a safety filter before tool execution (to be wired in orchestration).
