# Installs cert-manager and applies issuers, then reapplies ingress/certificate
param(
  [string]$RepoRoot = "."
)

$ErrorActionPreference = "Stop"

Write-Host "Installing cert-manager..."
kubectl apply -f "$RepoRoot/k8s/00-cert-manager.yaml"

Write-Host "Waiting for cert-manager pods..."
kubectl -n cert-manager rollout status deploy/cert-manager -w --timeout=180s
kubectl -n cert-manager rollout status deploy/cert-manager-webhook -w --timeout=180s
kubectl -n cert-manager rollout status deploy/cert-manager-cainjector -w --timeout=180s

Write-Host "Applying ClusterIssuers (staging and prod)..."
kubectl apply -f "$RepoRoot/k8s/cert-manager/cluster-issuer.yaml"

Write-Host "Re-applying Ingress and Certificate..."
kubectl apply -f "$RepoRoot/k8s/06-ingress.yaml"
kubectl apply -f "$RepoRoot/k8s/07-certificate.yaml"

Write-Host "Check certificate resources:"
kubectl -n q-ide get certificate,order,challenge
