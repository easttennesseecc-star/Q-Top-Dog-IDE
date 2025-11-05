# Common Incident Runbooks

These quick runbooks help responders mitigate and recover fast for frequent scenarios. Always follow the overarching FAILURE_REVIEW_PROCESS.md for complete steps, evidence, and RCA.

## 1) LLM Timeout Storm

Symptoms:
- Spikes in request latency and error rate
- Upstream LLM calls hit timeouts/retries; circuit breakers opening
- Token/cost SLIs may spike due to retries

Immediate actions:
1. Reduce blast radius
   - Enable feature flags to route a lower percentage of requests (canary) or temporarily switch to a fallback LLM.
   - Tighten request timeouts and lower retry counts in the LLM client.
   - Ensure circuit breakers are active.
2. Stabilize
   - Degrade gracefully: disable heavy chains or optional features.
   - If needed, temporarily pause regulated-domain features that are slow.
3. Validate
   - Confirm SLOs recover (latency/error rate).
   - Verify dashboards and Overwatch checks.
4. Evidence
   - Collect logs, request samples, and snapshot a representative workflow context.

Follow-up (RCA / prevention):
- Add adaptive timeout/backoff and better failover policy.
- Expand golden datasets to include slow-path scenarios.
- Tighten cost guardrails when retries surge.

## 2) Regulated-Domain Gate Bypass Alert

Symptoms:
- Overwatch or policy-as-code flags content generation in disallowed domains (e.g., medical/scientific)
- CI gates fail on responsible AI checks

Immediate actions:
1. Block and contain
   - Toggle edition/feature flags to enforce stricter regulated gating.
   - Ensure triad checks and Overwatch are mandatory for the affected routes.
2. Verify
   - Run the golden datasets and responsible AI tests locally/CI.
3. Trace
   - Identify the prompt chain or missing guard where the bypass occurred.
4. Evidence
   - Attach logs, offending prompts, decisions, and snapshot of the workflow.

Follow-up (RCA / prevention):
- Strengthen policy-as-code rules and add specific tests for the new pattern.
- Ensure UI clearly signals edition/gating state.
- Audit recent changes to triad or Overwatch integration.

## 3) Cost Spike (Token Burn)

Symptoms:
- Tokens per minute and $/min surge; budget alerts firing
- Heavy multi-LLM chains running concurrently

Immediate actions:
1. Throttle and cap
   - Lower per-request token budgets via config/feature flags.
   - Reduce parallelism and batch sizes; disable optional chain steps.
2. Swap to cheaper models where acceptable
   - Use dev-tier models in non-regulated flows temporarily.
3. Validate
   - Watch cost SLI dashboard; confirm slope normalizes.
4. Evidence
   - Capture representative prompts, chain configs, and cost metrics.

Follow-up (RCA / prevention):
- Add cost-aware routing and early stopping.
- Tighten default budgets and add preflight prompts estimation.
- Expand dashboards with per-feature and per-tenant cost attributions.

## 4) Retry Storm (Upstream Flapping)

Symptoms:
- Retry counters spike; elevated 5xx error rate
- Latency increases; circuit breakers toggling

Immediate actions:
1. Backoff aggressively
   - Increase jittered backoff; reduce max retries.
   - Enforce request hedging limits; disable idempotent retries if needed.
2. Failover policy
   - Shift traffic to alternate LLMs/providers.
3. Validate
   - Retry rate declines; error rate stabilizes.
4. Evidence
   - Logs with upstream status codes; retry decision traces.

Follow-up (RCA / prevention):
- Implement adaptive timeouts; preemptive failover on early signals.
- Add provider health checks into routing policy input.
- Add tests for retry storms in golden datasets.
