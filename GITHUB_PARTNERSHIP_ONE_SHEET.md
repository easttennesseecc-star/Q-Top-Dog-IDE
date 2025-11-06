# Top Dog + GitHub Copilot: Better Together — Partner One‑Sheet

Date: November 5, 2025
Audience: GitHub Copilot Partnerships, Alliances, Product

## Summary
Top Dog is a complementary IDE that runs GitHub at the center of the developer workflow. We integrate repos/PRs/Actions and add multi‑LLM BYOK, local/offline options, and reliability guardrails (build‑plan enforcement, contract tests, snapshot/rollback). Net: Copilot’s strengths + Top Dog’s guardrails = fewer failed PR cycles, faster merges, higher developer confidence.

## Value to GitHub
- Increase Copilot’s realized value per seat (fewer hallucination loops, smoother PR cycles)
- Expand Copilot reach into data science/game dev workflows (multi‑LLM, local models, media‑in‑IDE)
- Reduce churn drivers (predictable cost controls, BYOK flexibility, offline mode when needed)
- Keep customers anchored in GitHub (repos/PRs/Actions remain the system of record inside Top Dog)

## Joint Customer Value
- Speed: Multi‑LLM routing + guardrails reduce rework and failed PRs; merges happen faster
- Confidence: Build‑plan enforcement, contract tests, snapshot/rollback provide safe iteration
- Choice: BYOK to OpenAI/Anthropic and local models; privacy and latency options per team
- Cost control: Predictable subscriptions + customer‑owned usage keys; avoid hourly compute traps
- Integrated workflow: Media synthesis (Runway BYOK) alongside code; one place to ship

## Integration Architecture (High Level)
- GitHub App + OAuth with least‑privilege scopes; follow official APIs and rate limits
- Surface repos, PRs, reviews, and Actions status inside Top Dog panels (read‑only where possible)
- Use Checks/Statuses APIs for guardrail feedback (build‑plan adherence, contract test signals)
- Optional GitHub Actions templates to enable CI guardrails; no disruption to existing pipelines
- No scraping of private content; no training on customer code; data egress is customer‑controlled

## Compliance & Security Posture
- Health‑first routing, structured errors, snapshot/rollback safeguards (see RELIABILITY_CHECKLIST.md)
- BYOK keys remain customer‑owned; local‑first mode available; no unauthorized data persistence
- OAuth scopes minimized; periodic access review; signed GitHub App manifests
- We honor GitHub ToS and API rate limits; no automation that violates platform rules

## Commercial Options
- GitHub Marketplace listing with a free tier; optional Pro/Team pricing aligned to mutual success
- Co‑marketing: joint case studies demonstrating “Copilot + Top Dog” outcomes (merge speed, PR success)
- Co‑sell and solution briefs for data science and game dev verticals

## Partnership Asks & Offers
Asks (from GitHub):
- Partnership point of contact (alliances/BD) and product counterpart for technical review
- Guidance on Marketplace best practices and GitHub App review

Offers (from Top Dog):
- Complimentary Pro seats for GitHub partner teams evaluating the integration
- Joint content production (tutorials, webinars) targeting verticals where Copilot adoption can grow
- Migration and success playbooks for shared customers

## Next Steps
1) 20‑minute intro to align on partnership fit and success criteria
2) Technical review of integration surfaces (GitHub App scopes, PR checks, Actions templates)
3) 2‑3 design partners pilot (“Copilot + Top Dog”) and measure PR success and merge velocity

## Contacts
- Partnerships: partnerships@topdog.dev
- Product/Engineering: eng@topdog.dev
