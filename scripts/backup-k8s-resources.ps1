# Exports ConfigMaps and Secrets from the q-ide namespace into a timestamped folder
param(
  [string]$Namespace = "q-ide",
  [string]$OutDir = "backups"
)

$ErrorActionPreference = "Stop"
$ts = Get-Date -UFormat "%Y%m%d-%H%M%S"
$dest = Join-Path $OutDir "k8s-$Namespace-$ts"
New-Item -ItemType Directory -Force -Path $dest | Out-Null

Write-Host "Exporting ConfigMaps..."
kubectl -n $Namespace get configmaps -o name | ForEach-Object {
  $name = $_.Split('/')[1]
  kubectl -n $Namespace get configmap $name -o yaml > (Join-Path $dest "$name.configmap.yaml")
}

Write-Host "Exporting Secrets (base64 payloads) ..."
kubectl -n $Namespace get secrets -o name | Where-Object { $_ -notlike "*/default-token-*" } | ForEach-Object {
  $name = $_.Split('/')[1]
  kubectl -n $Namespace get secret $name -o yaml > (Join-Path $dest "$name.secret.yaml")
}

Write-Host "Done. Output at $dest"
