# SLI/SLO Definitions for Primary LLM Streaming

Endpoint scope: `/api/chat` (LLM streaming) and `/llm_stream` (legacy dev endpoint)

## SLIs
1) Latency
   - Metric: Time to First Token (TTFT) and total response time
   - Source: Prometheus histograms `llm_ttft_seconds`, `llm_response_seconds`

2) Error Rate
   - Metric: Percentage of requests that both return HTTP 200 and are NOT flagged by Overwatch
   - Source: `http_requests_total` (labels: endpoint,status) and `overwatch_flagged_total`

3) Availability
   - Metric: Successful traffic at the Ingress/Load Balancer (2xx)
   - Source: Prefer NGINX Ingress metrics; fallback: `http_requests_total` 2xx ratio

## SLOs (targets)
- Latency: 99% of requests complete < 1.5s (28d window). P95 ≤ 2s under expected load.
- Error Rate: 99.9% success (not flagged) over 7d.
- Availability: 99.99% per calendar month.

## Burn-rate Alerts
Following Google SRE best practices, we alert on error budget burn:
- High urgency: 2h window at 14.4× allowed error rate
- Warning: 1h window at 6× allowed error rate

Repo alert rules implement both HTTP error and Overwatch-flagged burn rates.

## Cost SLI (optional)
- Token cost per request (avg, p95) to watch budget drift
- Add counters by provider/model via middleware or chat route.
