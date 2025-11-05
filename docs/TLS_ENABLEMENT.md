# Enabling TLS with cert-manager (Let’s Encrypt)

This guide enables HTTPS for TopDog IDE on Kubernetes using cert-manager and NGINX Ingress.

Prerequisites:
- kubectl context targeting your cluster
- NGINX Ingress installed (see k8s/00-nginx-*.yaml)
- DNS A records for Top Dog.com, www.Top Dog.com, api.Top Dog.com pointing to the ingress load balancer

## 1) Install cert-manager

Apply CRDs and the cert-manager deployment (namespace: cert-manager):

```powershell
# From repo root
kubectl apply -f k8s/00-cert-manager.yaml
```

Verify pods:
```powershell
kubectl -n cert-manager get pods
```

## 2) Create ClusterIssuer (Let’s Encrypt)

We provide staging and production cluster issuers. Start with staging for validation, then switch to prod.

```powershell
kubectl apply -f k8s/cert-manager/cluster-issuer.yaml
```

Check issuers:
```powershell
kubectl get clusterissuer
kubectl describe clusterissuer letsencrypt-staging
kubectl describe clusterissuer letsencrypt-prod
```

## 3) Enable TLS in Ingress

Ingress `k8s/06-ingress.yaml` is annotated for cert-manager and includes a TLS section referencing secret `Top Dog-tls`.
Apply or re-apply the ingress:

```powershell
kubectl apply -f k8s/06-ingress.yaml
```

## 4) Request certificate

You can rely on the Ingress to trigger an issuance automatically or apply an explicit Certificate object:

```powershell
kubectl apply -f k8s/07-certificate.yaml
```

## 5) Validate issuance

Check challenges, orders, and certificate objects:

```powershell
kubectl -n Top Dog get certificate,order,challenge
kubectl -n Top Dog describe certificate Top Dog-tls
kubectl -n Top Dog get secret Top Dog-tls
```

Common issues:
- DNS not pointing to the ingress external IP.
- Ingress not reachable over HTTP for HTTP-01 challenge.
- Multiple ingresses responding for the same host.

## Rollback

If issuance fails repeatedly, switch to `letsencrypt-staging` in the ingress annotation to avoid rate-limits, fix issues, then switch back to `letsencrypt-prod`.

## Notes
- ConfigMap URLs (`k8s/01-configmap.yaml`) already use HTTPS.
- NGINX `ssl-redirect: "true"` is set in the ingress annotations.
