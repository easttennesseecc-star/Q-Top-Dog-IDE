# Top Dog IDE — Customer One‑Pager (Internal Handout)

Status: INTERNAL — DO NOT PUBLISH ONLINE
Updated: Nov 6, 2025

## What makes Top Dog different

AI Safety & Reliability
- OverWatch hallucination detection with real‑time severity metric (Prometheus)
- Consistency scoring across model runs
- Snapshot retention with verified RTO/RPO
- SLO burn‑rate quality gates in CI/CD
- PCG guardrails for game/media safety
- Red‑team runner for automated security checks

Compliance & Approvals
- Medical/scientific segment routing (HIPAA/FDA, RWE, multimodal)
- Human‑in‑the‑loop build plan approvals (with deviation monitoring)
- Program learning with clarifying questions before builds
- Persistent build rules via Build Manifest

Remote‑First Assistant
- SMS‑first approvals with MMS artifacts
- Linkless email commands (ACCEPT/DECLINE/MODIFY)
- Web Push + native push (OneSignal/FCM) with reminder failsafe
- Admin Message Board with instant triage

Multi‑LLM Orchestration
- BYOK for 53+ providers (no markup)
- Role‑based agents: Assistant, Builder, Tester, Security, Health Monitor
- Handoffs with validation gates and audit trail
- Prometheus/Grafana dashboards for safety/consistency/workflows

Media & Game Development
- AI media synthesis routes (image/video/audio)
- Multi‑engine integration (Construct 3, Godot, Unity, Unreal)
- AI Agent Marketplace (directory model)

## Comparison (Top Dog IDE vs GitHub Copilot)

Notes: This comparison focuses on built‑in product features. Copilot is strong for GitHub‑centric code suggestions and PR assistance but does not ship safety/approvals/compliance/BYOK orchestration as shown here.

| Category | Top Dog IDE | GitHub Copilot |
|---|---|---|
| Hallucination Detection | Yes (OverWatch) | Not offered |
| Consistency Scoring | Yes | Not offered |
| Medical/Scientific Routing | Yes | Not offered |
| Build Plan Approvals | Yes | Not offered |
| BYOK Multi‑LLM | Yes (53+) | Not the focus |
| Remote Approvals (SMS/Email/Push) | Yes | Not offered |
| Prometheus/Grafana Metrics | Yes | Not offered |

## Value & Deployment

Cost Control
- BYOK avoids per‑token markups
- Choose best model per task

Production‑Ready
- APIs wired in backend/main.py
- Tests and docs in repo

Run Anywhere
- Kubernetes + Helm deployment
- Web + native push options

## Sharing guidance

- This document is for internal or controlled handouts only.
- Do not host or link this comparison publicly.
- If a PDF is required, export this markdown locally and distribute directly.
