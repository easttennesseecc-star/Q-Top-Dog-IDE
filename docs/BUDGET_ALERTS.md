# Budget Alerts for LLM Spend

We expose two Prometheus counters to track spend:

- `llm_tokens_total{model,provider,direction}` — token counts (input/output)
- `llm_cost_usd_total{model,provider}` — accumulated USD cost

Costs are computed in the chat route using environment-configured rates:

- `COST_PER_1K_INPUT_<MODEL>` or fallback `COST_PER_1K_INPUT_<PROVIDER>`
- `COST_PER_1K_OUTPUT_<MODEL>` or fallback `COST_PER_1K_OUTPUT_<PROVIDER>`

Example (set via ConfigMap or Secret):

```
COST_PER_1K_INPUT_OPENAI=0.005
COST_PER_1K_OUTPUT_OPENAI=0.015
COST_PER_1K_INPUT_GEMINI=0.0025
COST_PER_1K_OUTPUT_GEMINI=0.005
```

Adjust to your contract rates. If unset, costs default to 0 and only token counts are tracked.

## Alerts

`monitoring/alert-rules.yaml` includes examples:

- `LLMCostSpendRateHigh` — sum rate of cost across all providers exceeds $/min threshold
- `LLMCostSpendRateHighProvider` — per-provider spend rate exceeds threshold

You can tune thresholds or add model-specific routes:

```
sum by (model) (rate(llm_cost_usd_total[15m])) > 1.0
```

## Dashboards

`monitoring/grafana-dashboard-topdog.yaml` includes a panel for cost per request:

```
(sum(rate(llm_cost_usd_total[5m]))) / (sum(rate(http_requests_total{endpoint="/api/chat"}[5m])))
```

This yields average USD/request over a sliding window.
