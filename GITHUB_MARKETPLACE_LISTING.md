# Top Dog IDE — Copilot Companion

Tagline: “Run GitHub inside Top Dog for faster merges and fewer failed PR cycles.”

## Short description
Top Dog is a complementary IDE for GitHub and Copilot. It keeps your repos/PRs/Actions GitHub‑native while adding multi‑LLM BYOK, local/offline options, and reliability guardrails (build‑plan enforcement, contract tests, snapshot/rollback) so teams ship faster with confidence.

## Long description
Top Dog integrates deeply with GitHub to reduce rework and accelerate PRs. Keep your GitHub repos, PRs, reviews, and Actions as the system of record—inside Top Dog panels—while gaining:

- Multi‑LLM routing and BYOK (OpenAI, Anthropic, etc.) plus local models
- Reliability guardrails: build‑plan enforcement, contract tests, snapshot/rollback
- Predictable costs with customer‑owned usage keys (avoid hourly compute traps)
- Media‑in‑IDE (Runway BYOK) to keep assets and code in one flow
- Local/offline mode for privacy, latency, and edge scenarios

“Copilot + Top Dog” = Copilot’s strengths + Top Dog’s guardrails → fewer failed PR cycles, faster merges, more confidence.

## Key benefits
- Faster merges: reduce PR back‑and‑forth with guardrail checks and clear plans
- Fewer rollbacks: snapshot/rollback protects main and mitigates risky changes
- Flexible models: route across providers or local models when needed
- Cost control: predictable subscription + BYOK usage, no surprise compute bills
- GitHub‑native: repos/PRs/Actions remain in GitHub; Top Dog adds visibility and safety

## How it works
1) Install the Top Dog GitHub App and select the repos you want
2) Open Top Dog and sign in with GitHub
3) Work normally—PRs, reviews, and Actions are surfaced in Top Dog
4) Guardrails (build‑plan/contract tests) report via Checks/Statuses on your PRs
5) Optional: enable BYOK multi‑LLM and local models from Top Dog settings

## Installation
- GitHub App installation (org or user): select repositories
- Minimal permissions (see Permissions section below)
- Optional GitHub Actions templates for CI guardrails (no pipeline disruption)

## Screenshots (placeholders)
- /assets/marketplace/screenshot-1.png — PR with guardrail checks
- /assets/marketplace/screenshot-2.png — Multi‑LLM BYOK settings
- /assets/marketplace/screenshot-3.png — Actions status inside Top Dog

## Pricing
- Free tier available; Pro starts at $12/user/month; Team/Enterprise available
- See `Q-IDE_MEMBERSHIP_TIERS_PRICING.md` for details

## Permissions
Repository permissions (minimum):
- Metadata: Read (required)
- Contents: Read (to display files/dirs in PR context)
- Pull requests: Read (to read PR metadata and head SHAs)
- Checks: Read & Write (to publish guardrail check runs)
- Commit statuses: Read & Write (to set status for guardrail signals)
- Actions: Read (to show workflow run status alongside PRs)

No Organization or Account permissions required for basic operation.

Subscribed events (webhooks):
- pull_request, check_suite, check_run, status, push, workflow_run (optional), installation_repositories

## Data handling & security
- We use only official GitHub APIs and honor rate limits/ToS
- We do not scrape private content or train on customer code
- BYOK keys remain customer‑owned; local‑first/offline modes available
- See `RELIABILITY_CHECKLIST.md` for health, rollback, and compliance guardrails

## Support
- Support: support@topdog.dev
- Docs: /docs (coming soon)

## Legal
- Terms of Service: https://topdog.dev/terms (placeholder)
- Privacy Policy: https://topdog.dev/privacy (placeholder)
