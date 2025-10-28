<#
PowerShell helper: install sample kubeconfig to user home with confirmation
Usage: Run from repo root (or update path to this script) in PowerShell:
  .\tools\kubec\install-sample-kubeconfig.ps1
#>
param(
  [switch]$Force
)

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
$sample = Join-Path $repoRoot 'tools\kubec\sample-kubeconfig.yaml'
$destDir = Join-Path $env:USERPROFILE '.kube'
$dest = Join-Path $destDir 'config'

if (-not (Test-Path $sample)) { Write-Error "Sample kubeconfig not found at $sample"; exit 2 }

if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir | Out-Null }

if ((Test-Path $dest) -and (-not $Force)) {
  $resp = Read-Host "A kubeconfig already exists at $dest. Overwrite? (y/N)"
  if ($resp -ne 'y' -and $resp -ne 'Y') { Write-Host 'Aborted by user.'; exit 0 }
}

Copy-Item -Path $sample -Destination $dest -Force
Write-Host "Sample kubeconfig installed to $dest"
Write-Host "You can also set the environment variable for the session:"
Write-Host "  $env:KUBECONFIG = '$sample'"
