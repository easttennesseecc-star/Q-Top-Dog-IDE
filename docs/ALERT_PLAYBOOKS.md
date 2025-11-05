# Alert Routing and Response Playbooks

This guide defines where alerts go and how to respond, based on burn-rate severity.

## Routing

Alert routing is configured via `monitoring/alertmanager-config.yaml` (AlertmanagerConfig CRD):

- `severity=page` → PagerDuty (critical, on-call)
- `severity=warn` → Slack `#alerts` (triage, during business hours)
- Default → Email to oncall@example.com

Replace receivers with your channels and wire secrets in the `alertmanager-secrets` Secret (PagerDuty routing key, Slack webhook, SMTP password).

## Burn-rate Severity and Runbooks

We use a standard SLO error budget policy:

- Page when 2h burn-rate > 14.4x (SLO breach risk)
- Warn when 1h burn-rate > 6x (early warning)

### Backend Error Budget Burn

1. Acknowledge alert; check recent deploys and error logs
2. Roll back canaries/disable risky feature flags
3. Check upstream LLM provider status and swap to secondary if needed
4. Verify recovery and update incident ticket

### Overwatch-Flagged Burn

1. Inspect flagged responses; identify pattern (domain, prompt type)
2. Enable stricter profiles or add disclaimers for affected routes
3. If provider-specific, flip triad to safer model
4. Run regression prompts from golden set; close when stable

### High LLM Spend Rate

1. Identify offending provider/model in Prometheus: `sum by (provider,model) (rate(llm_cost_usd_total[5m]))`
2. Reduce temperature/max tokens; enable caching; prefer cheaper models
3. Gate heavy features behind PRO/Enterprise
4. Set temporary rate limits; follow up with prompt and model tuning

## Incident Lifecycle

- Declare incident in shared channel
- Assign Incident Commander (IC) and Ops Liaison
- Timeline updates every 15–30 minutes while paging alerts are firing
- Post-incident review within 72 hours
