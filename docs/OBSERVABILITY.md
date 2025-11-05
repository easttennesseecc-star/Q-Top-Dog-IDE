# Observability: Prometheus, Grafana, and SLOs

## What’s included
- Pod annotations for scraping (see `k8s/04-backend.yaml`)
- `/metrics` endpoint in backend (Prometheus exposition)
- `monitoring/servicemonitor-backend.yaml` for Prometheus Operator
- `monitoring/alert-rules.yaml` with example burn‑rate alerts

## Install Prometheus & Grafana (recommended)
- Use kube‑prometheus‑stack (Helm chart `prometheus-community/kube-prometheus-stack`)
- Apply the ServiceMonitor and PrometheusRule after installation

## Dashboards
Suggested panels:
- Request rate, error rate, latency (RED method)
- Chat P95/P99 latency and throughput
- Saturation: CPU/memory, HPA behavior, pod restarts

## SLOs and Alerts
Baseline SLOs:
- Availability: 99% monthly for chat endpoints
- Latency: P95 ≤ 2s under expected load

Alerts (burn‑rate examples in repo):
- Page when 2h burn rate > 14.4× budget; warn when 1h > 6×

## Validation
- Verify `/metrics` responds (200, content-type Prometheus)
- Check Prometheus targets show backend as “UP”
- Confirm alerts fire under induced error conditions
