# GitHub App: Minimal Permissions & Events (Fast‑Track Review)

Goal: Keep permissions as low as possible while enabling PR surfacing and guardrail feedback.

## App metadata
- App name: Top Dog IDE (placeholder)
- Homepage URL: https://topdog.dev (placeholder)
- Callback URL: https://topdog.dev/api/github/callback (placeholder)
- Webhook URL: https://topdog.dev/api/github/webhook (placeholder)
- Webhook secret: set in GitHub; stored encrypted server‑side

## Repository permissions (minimum viable)
- Metadata: Read (required by all apps)
- Contents: Read — display repo tree/files in PR context (no write)
- Pull requests: Read — read PR metadata, head/base SHAs, reviews summary
- Checks: Read & Write — create check runs for guardrails (build‑plan, contract tests)
- Commit statuses: Read & Write — set status contexts when checks aren’t available
- Actions: Read — show workflow/run status in context (no write/dispatch)

Not requested:
- Issues, Discussions, Secrets, Webhooks (writes), Administration — not needed
- Code write or Actions write/dispatch — not needed

## Organization permissions
- None required for core features

## Account permissions
- None required for core features

## Events (webhooks)
- pull_request — react to PR open/sync/close events
- check_suite, check_run — correlate guardrail checks
- status — capture legacy status updates
- workflow_run (optional) — surface Actions workflow results
- push — update context on new commits to PR branches
- installation_repositories — track repo add/remove for installations

## Token usage
- Use installation access tokens scoped to selected repositories
- No classic OAuth scopes; we avoid full‑repo OAuth tokens
- Optional user‑to‑server flow (GitHub App) for identity only (no extra permissions)

## Data access boundaries
- No training on customer code; no scraping; no third‑party sharing
- Retain minimal PR metadata (ids, SHAs, check statuses) for UI; expire logs routinely
- BYOK model keys are customer‑owned; Top Dog never shares keys with third parties

## Review notes for GitHub
- Purpose: surface GitHub PRs/Actions inside Top Dog and write guardrail check results
- Justification: each permission maps to specific UI/guardrail uses; no write access to code/branches
- Safety: health‑first backend, structured errors, snapshot/rollback; see `RELIABILITY_CHECKLIST.md`
- Contact: security@topdog.dev, eng@topdog.dev
