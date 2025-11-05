# Grafana Dashboards

We ship a starter SLO dashboard as a ConfigMap: `monitoring/grafana-dashboard-topdog.yaml`.

When using kube-prometheus-stack, ConfigMaps with label `grafana_dashboard=1` are auto-discovered and imported by the Grafana sidecar.

Panels included:

- TTFT p90 (llm_ttft_seconds)
- Response latency p90 (llm_response_seconds)
- Overwatch flagged ratio
- Cost per request (USD)

Import popular RED/SLO dashboards from the Grafana catalog as well, then complement them with our LLM-specific panels above.
