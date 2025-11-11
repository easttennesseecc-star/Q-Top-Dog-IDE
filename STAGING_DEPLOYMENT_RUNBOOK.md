# Staging Environment Runbook

This runbook describes how to deploy and operate the dedicated staging environment for Q-Top-Dog-IDE.

## Overview
- Namespace: `topdog-staging`
- Domains:
  - Frontend: https://staging-app.topdog-ide.com
  - Backend API: https://staging-api.topdog-ide.com
- Certificates: cert-manager with `letsencrypt-staging` ClusterIssuer
- Container registry: GHCR (ghcr.io) with images tagged `:staging` and by commit SHA

## Prerequisites
- Kubernetes cluster accessible from CI and your workstation
- cert-manager installed and `letsencrypt-staging` ClusterIssuer configured
- GHCR access (defaults to public via GitHub Actions GITHUB_TOKEN; use GHCR_PAT if your images are private)
- DNS provider access (to create A/AAAA/CNAME records)

## One-time setup
1. DNS
   - Point `staging-app.example.com` to your ingress controller LB IP/hostname
   - Point `staging-api.example.com` to the same LB
2. Create namespace and base objects
   - From the repo root:
     - kubectl apply -f deploy/k8s/staging/namespace.yaml
     - kubectl apply -f deploy/k8s/staging/configmap.yaml
     - kubectl apply -f deploy/k8s/staging/secrets.yaml (edit placeholders first)
3. Certificates
   - Ensure cert-manager is issuing for the staging domains; the ingress will request certs automatically
4. Image pull secret (only if GHCR private)
   - Create secret `ghcr-pull` in `topdog-staging` and patch default SA; the CI workflow handles this if GHCR_PAT is provided

## CI/CD deployment (recommended)
- Workflow: .github/workflows/deploy-staging.yml
- Secrets required:
  - STAGING_KUBECONFIG_B64: base64-encoded kubeconfig with access to the cluster
  - GHCR_PAT: Personal Access Token with package:write (optional if images are public)
- Triggers: Push to `staging` branch or manual “Run workflow”
- Steps performed:
  - Build and push frontend and backend images to GHCR with `:staging` and `:${{ github.sha }}` tags
  - Apply namespace/config/secrets/services/deployments/ingress
  - Patch deployments to use the `${{ github.sha }}` images
  - Wait for rollout and smoke-test /health

## Manual deployment (optional)
- Build and push images locally or via scripts
- Apply manifests:
  - kubectl apply -f deploy/k8s/staging/
  - kubectl -n topdog-staging set image deployment/qide-frontend frontend=ghcr.io/OWNER/REPO/qide-frontend:<TAG>
  - kubectl -n topdog-staging set image deployment/qide-backend backend=ghcr.io/OWNER/REPO/qide-backend:<TAG>

## Configuration
- Update `deploy/k8s/staging/configmap.yaml` with the final staging URLs
- Update `deploy/k8s/staging/secrets.yaml` with:
  - JWT_SECRET (unique value for staging)
  - Stripe keys (test keys) if Stripe is enabled
  - OAuth client secrets for staging origins

## Health and smoke tests
- API health: curl -fsS https://staging-api.topdog-ide.com/health
- Frontend basic check: open https://staging-app.topdog-ide.com in a browser
- In-cluster rollout status:
  - kubectl -n topdog-staging rollout status deployment/qide-backend
  - kubectl -n topdog-staging rollout status deployment/qide-frontend

## Rollback
- To previous working image:
  - kubectl -n topdog-staging rollout undo deployment/qide-frontend
  - kubectl -n topdog-staging rollout undo deployment/qide-backend
- Or set image explicitly to a known good SHA:
  - kubectl -n topdog-staging set image deployment/qide-frontend frontend=ghcr.io/OWNER/REPO/qide-frontend:<GOOD_SHA>
  - kubectl -n topdog-staging set image deployment/qide-backend backend=ghcr.io/OWNER/REPO/qide-backend:<GOOD_SHA>

## Notes and best practices
- Keep staging JWT secrets and OAuth/Stripe test keys separate from production
- Use staging-specific OAuth redirect URIs and allowed origins
- If using cert-manager staging issuer, expect test certificates; switch to `letsencrypt-prod` when ready
- Consider adding a staging banner in the UI via WORKSPACE_PROFILE=staging to avoid confusion
