# 4–6 Week Nonclinical Pilot Plan

This plan hardens TopDog IDE for a research-oriented pilot with safety, reliability, and observability.

## Scope (Pilot)
- Enable TLS via cert-manager and enforce HTTPS
- Lock down CORS/CSP; add NGINX rate limiting
- External Secrets (or Vault) for secret management + rotation
- Enforce backend tests in CI (fail on error), include RTO/RPO suite
- Upgrade Overwatch to use a dedicated verification model via env/secrets
- Observability: Prometheus + Grafana with SLO and burn-rate alerts

## Tasks and Owners
1) TLS
   - Install cert-manager; apply ClusterIssuer; reapply Ingress and Certificate
   - Verify green padlock; no mixed content
   - Reference: `docs/TLS_ENABLEMENT.md`, `scripts/deploy-cert-manager.ps1`

2) CORS/CSP + Rate limiting
   - Configure CORS via `CORS_ORIGINS` in `k8s/01-configmap.yaml`
   - CSP via `CSP_POLICY` env; backend sets header automatically
   - NGINX rate limiting in `k8s/06-ingress.yaml` (limit-rps/burst/connections)

3) Secrets and rotation
   - Install External Secrets Operator (ESO)
   - Configure `k8s/secrets/external-secret.yaml` to sync secrets into `Top Dog-secrets`
   - Rotate API keys (OpenAI/Anthropic/Google) and DB/Stripe secrets
   - Reference: `docs/SECRETS_MANAGEMENT.md`

4) CI test enforcement
   - GitHub Actions now installs `backend/requirements.txt` and runs `pytest` (no continue-on-error)
   - Includes `backend/tests/test_claims_rto_rpo.py` for RTO/RPO targets

5) Overwatch (verification model)
   - Set `DEFAULT_OVERWATCH_LLM` or domain overwatch vars `MED_OVERWATCH_LLM`, `SCIENCE_OVERWATCH_LLM`
   - Ensure provider API keys are present via secrets
   - Overwatch emits verification event in chat stream

6) Observability (SLIs/SLOs, alerts)
   - Backend exposes `/metrics` (Prometheus)
   - Apply `monitoring/servicemonitor-backend.yaml` and `monitoring/alert-rules.yaml`
   - Stand up Grafana dashboards (latency, error rate, saturation)
   - Target: P95 chat latency ≤ 2s under expected load

## Success Criteria
- Zero critical safety findings across golden set + 10–20 real lab prompts
- ≤ 2s P95 chat latency under expected load; no unplanned downtime
- TLS: green padlock, no mixed content, CSP reports clean
- DR drill: backup + restore verified within RTO/RPO targets

## Verification Checklist
- [ ] HTTPS only; redirects from HTTP
- [ ] CORS limited to allowed origins; CSP active and effective
- [ ] Secrets synced by ESO; rotation playbook executed
- [ ] CI fails on backend test regressions; RTO/RPO green
- [ ] Prometheus scraping `/metrics`; Grafana SLO dashboards and burn-rate alerts active

## Rollback and Risk Mitigation
- Use canary or surge/rolling updates; keep previous image available
- Feature flags for risky toggles (e.g., Overwatch strict mode)
- Disable rate limiting on false positives by host/path-scoped annotation override
