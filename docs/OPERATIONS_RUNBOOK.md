## Operations Runbook — TopDog/Q‑IDE Kubernetes

This runbook summarizes probe timings, common K8s symptoms, and first-response steps for a healthy, self-healing service.

### Service Overview
- App: FastAPI backend (uvicorn) with explicit `/health` endpoint registered before all other routes.
- Self-healing: Startup/Liveness/Readiness HTTP probes on `/health`; HPA enabled with cost-aware limits; PodDisruptionBudget when replicas > 1.
- Canonical redirect and compliance middleware skip `/health` and other monitoring paths.

### Probe Settings (values-qide.yaml)
- readinessProbe: path=/health, initialDelay=15s, period=10s, timeout=5s, failureThreshold=3
- livenessProbe: path=/health, initialDelay=20s, period=10s, timeout=5s, failureThreshold=3

### Common Symptoms and Actions

1) ImagePullBackOff
- Symptom: Pod stuck pulling image; describe shows auth errors.
- Action: Create/update DOCR pull secret in the target namespace and ensure `imagePullSecrets` references it.
- Verify:
  - kubectl get secret docr-secret -n topdog
  - helm upgrade --install topdog deploy/helm/topdog -f deploy/helm/topdog/values-qide.yaml -n topdog

2) CrashLoopBackOff
- Symptom: Container repeatedly restarts.
- Causes:
  - `/health` not reachable (404/redirect), causing probe failures.
  - Missing env or secret; application exits on error.
- Action:
  - kubectl logs <pod> -n topdog --previous --tail=200
  - Confirm health route exists and is excluded from redirects; ensure secrets mounted.
  - Adjust probe delays/timeouts if startup is slow.

3) Readiness never true
- Symptom: Pod Running but not Ready; service not routing traffic.
- Action:
  - kubectl describe pod <pod> -n topdog to see probe failures.
  - Confirm `/health` returns 200 in cluster:
    - kubectl run curl --rm -i --restart=Never --image=curlimages/curl:8.8.0 -n topdog -- -sS http://topdog-topdog:8000/health

4) 308 redirect loops or 404 on `/health`
- Ensure `ENABLE_HOST_REDIRECT` excludes `/health` and internal hosts.
- Ensure frontend catch-all is mounted after API routers.

### Scaling and Availability
- HPA: min=1, max=5, CPU target=80%, Memory target=85% (tuned for cost).
- PDB: minAvailable=1 (enabled when maxReplicas > 1) to reduce disruptions.

### Routine Checks
- kubectl get pods -n topdog
- kubectl get hpa -n topdog
- kubectl logs deploy/topdog-topdog -n topdog --tail=200
- In-cluster health:
  - kubectl run curl --rm -i --restart=Never --image=curlimages/curl:8.8.0 -n topdog -- -sS http://topdog-topdog:8000/health

### Rollout
- Bump image tag in `deploy/helm/topdog/values-qide.yaml`.
- docker build/tag/push to DOCR.
- helm upgrade --install topdog ... -n topdog
- Watch pods: kubectl get pods -n topdog -w

### Rollback
- helm history topdog -n topdog
- helm rollback topdog <REVISION> -n topdog

### Contacts
- Secrets: `docr-secret` (DOCR pull), `provider-api-keys` (app secrets)
- Ingress: NGINX with cert-manager; cert on secret `topdog-tls`
