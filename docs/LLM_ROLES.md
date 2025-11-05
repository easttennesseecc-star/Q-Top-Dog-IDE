# LLM Roles – Architecture and Safety

Purpose: Standardize role behaviors, prompts, and model mappings to reduce hallucinations and improve reliability.

## Roles
- Architect: decomposes tasks, drafts specs, proposes data models and APIs; outputs checklists and acceptance tests
- Coder: implements code to spec; cites files changed; requests missing context explicitly
- Reviewer: static analysis, test coverage gaps, security lint, clarity; suggests minimal diffs
- Tester: writes/updates unit + e2e tests; covers happy path + edge cases; green-before-merge
- Deployer: builds images, updates manifests, runs rollout, verifies health and SLOs

## Model Mapping (examples)
- Architect/Reviewer: Claude Sonnet / GPT-4o (analysis)
- Coder: GPT-4o mini / Sonnet small (cost-performance)
- Tester: Code-specialized model if available
- Deployer: Lightweight model + shell/tool plugins

## Safety & Hallucination Controls
- Contract-first: each role emits a 3–4 bullet contract (inputs/outputs/error modes/success criteria) before work
- Source-of-truth checks: link to code lines or files when asserting a feature exists
- Gating: documentation claims cannot be ✅ without proof (tests, logs, screenshots)
- Policy prompts: embed anti-hallucination reminders in role prompts (verify before claim; cite evidence)

## Implementation Hints
- Centralize prompts per role in code for maintainability
- Add a small role router component that selects model by task type and cost budget
- Log role outputs with metadata (role, model, cost, tokens, latency) for analytics
