# Deploying Dev vs Regulated Editions

We use Kustomize overlays to toggle regulated features without forking the codebase.

## Prerequisites
- Base manifests in `k8s/` are applied by both editions
- kube-prometheus-stack + ingress-nginx recommended

## Dev Edition (software/game dev)
- Fast, simple, minimal constraints
- Overwatch is opt-in only via `X-Overwatch-LLM`

Apply:

```
kubectl apply -k k8s/overlays/dev
```

## Regulated Edition (medical/science)
- Domain triads + default Overwatch
- Optional hard blocking when verification fails
- Disclaimer appended automatically

Apply:

```
kubectl apply -k k8s/overlays/regulated
```

## What changes between editions
- `ENABLE_REGULATED_DOMAINS` (on/off)
- `REQUIRE_OVERWATCH` (on in regulated)
- `BLOCK_ON_OVERWATCH_FAIL` (on in regulated)
- `FORCE_DISCLAIMER_TEXT` (string in regulated)
- `DEFAULT_OVERWATCH_LLM` (set in regulated)

See also `docs/EDITIONS_AND_PROFILES.md` for behavior details.
