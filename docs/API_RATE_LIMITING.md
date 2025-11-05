# API Rate Limiting: OPA/Envoy vs NGINX Plugin

This document outlines two viable stacks for enforcing API rate limiting as policy‑as‑code and how to wire the existing `policies/api/rate_limit.rego` file.

## Option A: Envoy + OPA (Ext AuthZ / WASM)

- Envoy acts as the gateway/proxy in front of the backend.
- OPA runs as a sidecar or external service. Envoy calls OPA for policy decisions.
- Pros: First‑class policy evaluation, rich attributes, compatible with service mesh (Istio/Consul).
- Cons: More moving parts vs NGINX.

Wiring sketch:
- Configure Envoy External Authorization (ext_authz) to query OPA.
- Map request attributes to OPA input:
```jsonc
{
  "api_key": "<from header>",
  "path": "/api/v1/...",
  "method": "GET",
  "rate": { "requests_per_min": <value from rate counter> }
}
```
- Evaluate `data.topdog.api.allow` in `policies/api/rate_limit.rego`.
- Deny on `data.topdog.api.deny` non‑empty.

## Option B: NGINX + Lua/OPA plugin

- NGINX ingress with OpenResty/Lua or OPA plugin for authz.
- Pros: Pair well with K8s Ingress; simple deployment.
- Cons: Less native observability than Envoy.

Wiring sketch:
- Inject Lua phase to compute current request rate (per API key or IP) using a shared dict or Redis.
- Build an input JSON matching the Rego policy shape and call OPA (local sidecar) or embed simple Lua logic mirroring the policy.
- Deny when over limit; emit metrics labels (api_key, path).

## Metrics and decisions
- Emit Prometheus counters for allow/deny per key and endpoint.
- Create alerts on sustained deny rates and throttling anomalies.

## Next steps
1. Choose gateway (Envoy if using service mesh; otherwise NGINX ingress is fine).
2. Plumb API key extraction and per‑tenant counters.
3. Feed the counters into policy input and evaluate `policies/api/rate_limit.rego`.
4. Add dashboards for allow/deny and per‑tenant throughput; set SLOs and alerts.
