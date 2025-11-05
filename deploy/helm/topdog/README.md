# Top Dog (Aura) Helm Chart

This chart deploys the Top Dog (Aura) application on Kubernetes with optional autoscaling and ingress.

## Values

Key settings in `values.yaml`:
- `replicaCount`: desired replicas (default 2)
- `image.repository`, `image.tag`: container image
- `service.port`: container HTTP port (default 8080)
- `env.MARKETPLACE_MODE`: set to `directory` (BYOK directory model)
- `autoscaling.*`: HPA settings
- `ingress.*`: NGINX ingress configuration and TLS

## Install

PowerShell example commands:

```powershell
# Create namespace (optional)
kubectl create namespace topdog -o yaml 2>$null | Out-Null

# Install or upgrade the release
helm upgrade --install topdog ./topdog `
  --namespace topdog `
  --set image.repository="ghcr.io/your-org/topdog" `
  --set image.tag="v1.0.0" `
  --set env.MARKETPLACE_MODE=directory `
  --set ingress.enabled=true `
  --set ingress.hosts[0].host="topdog.example.com" `
  --set ingress.tls[0].secretName="topdog-tls" `
  --set ingress.tls[0].hosts[0]="topdog.example.com"
```

## Notes

- Provider API keys should be stored in Kubernetes Secrets and referenced via `values.yaml` `extraEnvFrom`.
- Liveness and readiness probes default to `/healthz` and `/readyz`; adjust if your app uses different endpoints.
- For DigitalOcean Kubernetes (DOKS), ensure NGINX Ingress and cert-manager are installed.
