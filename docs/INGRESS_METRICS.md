# NGINX Ingress Controller Metrics

To measure availability at the load balancer (edge), enable Prometheus metrics in your ingress controller and scrape them.

## Enable metrics on ingress-nginx

If you install ingress-nginx via Helm, set:

- controller.metrics.enabled=true
- controller.metrics.serviceMonitor.enabled=true (if using kube-prometheus-stack)

Example Helm values snippet:

```
controller:
  metrics:
    enabled: true
    service:
      annotations: {}
      port: 10254
      targetPort: 10254
```

On managed clusters (e.g., DigitalOcean), ensure the controller is started with `--enable-prometheus-metrics`, and a Service exposes port 10254 named `metrics`.

## ServiceMonitor

We include `monitoring/servicemonitor-ingress.yaml` which selects the controller Service by labels:

- app.kubernetes.io/name: ingress-nginx
- app.kubernetes.io/component: controller

Adjust labels/namespace if your controller differs.

## Availability SLI

Use the built-in request counters from the controller to compute availability:

- Success proxying: all requests
- Errors: 5xx from backend or LB

PromQL example (5-minute window):

```
1 - (sum(rate(nginx_ingress_controller_requests{status=~"5.."}[5m])) / sum(rate(nginx_ingress_controller_requests[5m])))
```

Alerting rules can be added similarly to backend SLO burn rules.
