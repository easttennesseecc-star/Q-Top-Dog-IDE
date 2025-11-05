# TLS Restoration Playbook (DigitalOcean Kubernetes)

Goal: Restore HTTPS for Top Dog.com, www.Top Dog.com, and api.Top Dog.com using cert-manager + Let’s Encrypt.

Prereqs
- kubectl configured for the target DigitalOcean cluster
- Helm installed locally
- DNS A records for Top Dog.com, www.Top Dog.com, api.Top Dog.com pointing to the NGINX Ingress LB IP

## 1) Install cert-manager (controller + CRDs)

```powershell
# Add repo
helm repo add jetstack https://charts.jetstack.io ; helm repo update

# Install a recent cert-manager (adjust version if needed for your cluster)
helm upgrade --install cert-manager jetstack/cert-manager `
  --namespace cert-manager `
  --create-namespace `
  --set crds.enabled=true `
  --version v1.15.0

# Verify
kubectl get pods -n cert-manager
kubectl get crds | Select-String -Pattern cert-manager
```

## 2) Create ClusterIssuers (staging + prod)

Apply `k8s/cert-manager/cluster-issuer.yaml` after editing the email address.

```powershell
kubectl apply -f k8s/cert-manager/cluster-issuer.yaml
kubectl get clusterissuer
```

## 3) Re-enable TLS in Ingress

Update your `k8s/06-ingress.yaml`:
- Add annotation: `cert-manager.io/cluster-issuer: letsencrypt-prod`
- Add `tls:` section for the hosts (Top Dog.com, www.Top Dog.com, api.Top Dog.com) using a single secretName e.g. `Top Dog-tls`

```yaml
metadata:
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
    - hosts:
        - Top Dog.com
        - www.Top Dog.com
      secretName: Top Dog-tls
    - hosts:
        - api.Top Dog.com
      secretName: Top Dog-tls
```

Apply and verify:

```powershell
kubectl apply -f k8s/06-ingress.yaml
kubectl describe certificate -A
kubectl get challenges.acme.cert-manager.io -A
```

## 4) Troubleshooting
- If you see ACME HTTP-01 challenges failing, ensure NGINX Ingress is routing `/.well-known/acme-challenge/` paths.
- If strict decoding errors occur on issuers, confirm the controller is installed (Step 1) and YAML apiVersions are correct.
- Use Let’s Encrypt staging first to avoid rate limits; switch to prod after success.
