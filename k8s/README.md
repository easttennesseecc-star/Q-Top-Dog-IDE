# Kubernetes deployment for Topdog IDE backend

This folder contains manifests to deploy the FastAPI backend behind an NGINX Ingress with TLS from cert-manager.

## Prerequisites
- Kubernetes cluster with NGINX Ingress Controller
- cert-manager installed with a ClusterIssuer named `letsencrypt-prod`
- DNS A/AAAA records for `topdog-ide.com` and `www.topdog-ide.com` pointing to the ingress controller
- A container image available at `ghcr.io/easttennesseecc-star/q-top-dog-ide:latest`

## Secrets
Create a secret with any required keys referenced by the deployment (adjust as needed):

kubectl create secret generic topdog-ide-secrets \
  --from-literal=DEV_SEED_KEY=disabled-in-prod \
  --from-literal=DEV_FUNDS_KEY=disabled-in-prod

Note: Do not enable dev seeding endpoints in production.

## Storage
A PersistentVolumeClaim named `topdog-ide-data` stores the SQLite database at `/app/data/topdog_ide.db`.

Apply the PVC:

kubectl apply -f pvc.yaml

## Deploy
Apply the deployment, service, and ingress:

kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml

Check rollout and ingress:

kubectl rollout status deploy/topdog-ide-backend
kubectl get ingress topdog-ide -o wide

## Health and docs
- Health: https://topdog-ide.com/health
- OpenAPI docs: https://topdog-ide.com/docs

## Aura programs (profiles)
Topdog‑ide supports distinct Aura programs and data‑safeguard profiles:

- Dev (general): fast iteration profile for general development
- Medical: regulated profile with stricter safeguards
- Scientific: regulated profile tailored for scientific work

These are exposed via environment flags already used by the backend:

- ENABLE_REGULATED_DOMAINS=true enables the regulated posture (medical/scientific)
- X-Data-Segment header (or defaults) selects a data segment: general, medical, scientific

In Kubernetes, you can pin a default segment by setting an env var on the Deployment:

  - DEFAULT_DATA_SEGMENT=medical or scientific

Frontends and internal tools can switch between programs without separate clusters by adjusting headers and env, while documentation and branding remain under “Topdog‑ide” across all programs.
