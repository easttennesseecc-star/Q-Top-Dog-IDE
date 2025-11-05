# Build & Release Pipeline – Flawless From Dev to Prod

Objectives
- Reproducible builds, security scanning, automated tests, safe rollout, and fast rollback

## CI (GitHub Actions)
Jobs
1) lint-and-typecheck: ESLint/TS/flake8/mypy
2) unit-tests: frontend (vitest), backend (pytest)
3) build-images: docker buildx, tag ghcr.io, push on main and tags
4) sast: CodeQL or Semgrep
5) container-scan: Trivy on images
6) e2e: Playwright smoke against preview environment

Artifacts
- Docker images: ghcr.io/<org>/Top Dog-frontend:<sha>, Top Dog-backend:<sha>
- SBOMs and scan reports uploaded to Actions artifacts

## CD
- K8s deployment via GitHub Actions with a protected environment
- Blue/green or canary rollout (progressive delivery), with health and error budgets
- Automatic rollback on failure signals (5xx spikes, readiness timeouts)

## Config
- Runtime env injection for frontend (env.js); backend via ConfigMaps/Secrets
- Separate staging vs production namespaces and ClusterIssuers

## Observability Gates
- Post-deploy checks: uptime ping, key route probes, error budget fitness
- Notify: Slack/Teams with summary and links (Grafana/Sentry)

## Secrets
- Store in GitHub Actions secrets or external vault; never in repo
