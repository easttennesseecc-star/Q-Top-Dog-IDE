# Secrets Management and Rotation

This project supports External Secrets Operator (ESO) to sync secrets from a managed store into Kubernetes secrets consumed by the app.

## Install External Secrets Operator
Follow the official docs for your cluster:
- https://external-secrets.io/latest/introduction/getting-started/

Example (helm):
- Install CRDs and controller in `external-secrets` namespace
- Create a `ClusterSecretStore` referencing your provider (AWS Secrets Manager, GCP Secret Manager, Azure Key Vault, 1Password, etc.)

## Configure ExternalSecret
- Update `k8s/secrets/external-secret.yaml` to match your secret paths
- Apply it: `kubectl apply -f k8s/secrets/external-secret.yaml`
- ESO will populate the `Top Dog-secrets` Secret with keys:
  - DATABASE_PASSWORD, JWT_SECRET
  - STRIPE_SECRET_KEY, STRIPE_WEBHOOK_SECRET, STRIPE_PUBLISHABLE_KEY
  - OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY

## Application Wiring
- Workloads already consume `Top Dog-secrets` via `envFrom`/`secretKeyRef` in `k8s/04-backend.yaml`
- Overwatch can use provider keys for verification models (set domain overwatch LLM names in ConfigMap)

## Rotation Playbook
1) Write new secret value to the external store (versioned)
2) Verify ESO syncs it (check `kubectl get secret Top Dog-secrets -n Top Dog -o yaml`)
3) Restart Deployments that cache secrets in memory (or let rolling update pick it up)
4) Validate functionality (Overwatch calls, Stripe webhooks, DB connectivity)

## Notes
- Avoid committing `k8s/02-secrets.yaml` with live values; prefer ExternalSecret
- Scope provider IAM to least privilege for secrets access
