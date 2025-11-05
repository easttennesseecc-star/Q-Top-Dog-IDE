# Hallucination Prevention – Enforcement Layer

This complements `AI_HALLUCINATION_PREVENTION_FRAMEWORK.md` with concrete gates and tools.

## Enforcement Gates
- Code Evidence Gate: Any doc claim about a feature must include a reference (file/function/route) or a test proving it
- Runtime Evidence Gate: For deployed claims, attach logs, screenshots, or URLs
- Verification Labeling: Use 🟡 until evidence is attached; only then flip to ✅
- PR Template: Add a checklist requiring evidence links for new/updated claims

## Tooling
- Docs linter: CI job that fails PRs if claims lack evidence footnotes
- Test coverage threshold per area (agents, billing, auth, LLM orchestration)
- Link checker for internal docs

## Process
- Weekly doc audit: remove or downgrade unverified claims
- Role prompts (Reviewer): reject changes that add claims without sources

## Security/Compliance Extensions
- Require data flow diagrams for features handling PII/PHI
- Retain audit logs for doc approvals and changes
