<#
Automated setup for kubec development environment.

What this does:
  - Backs up any existing user kubeconfig at %USERPROFILE%\.kube\config to config.bak.TIMESTAMP
  - Copies repo sample kubeconfig into %USERPROFILE%\.kube\config
  - Runs `npm install` in tools/kubec
  - Optionally runs `npm link` to make `kubec` available globally
  - Optionally starts the local dev server (tools/kubec/server.js) in the background

Usage (from repo root or anywhere):
  # dry-run (shows what will happen)
  .\tools\kubec\setup-kubec.ps1 -WhatIf

  # perform setup, don't auto-start server
  .\tools\kubec\setup-kubec.ps1

  # perform setup, link the CLI, and start server
  .\tools\kubec\setup-kubec.ps1 -NpmLink -AutoStartServer

Notes:
  - This script will ALWAYS create a backup of an existing kubeconfig before overwriting.
  - Running `npm link` requires Node.js/npm available on PATH and may modify your global npm links.
  - Starting the server will run `node tools\kubec\server.js` as a detached process.
#>

param(
  [switch]$NpmLink,
  [switch]$AutoStartServer,
  [switch]$Force
)

$ErrorActionPreference = 'Stop'

Write-Host "Running kubec automated setup..."

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$repoRoot = Resolve-Path -Path (Join-Path $scriptDir '..')
$sample = Join-Path $scriptDir 'sample-kubeconfig.yaml'

if (-not (Test-Path $sample)) {
  Write-Error "Sample kubeconfig not found at $sample"; exit 2
}

$destDir = Join-Path $env:USERPROFILE '.kube'
if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir | Out-Null }
$dest = Join-Path $destDir 'config'

if (Test-Path $dest) {
  $timestamp = Get-Date -Format 'yyyyMMddHHmmss'
  $bak = "$dest.bak.$timestamp"
  Write-Host "Backing up existing kubeconfig to $bak"
  Copy-Item -Path $dest -Destination $bak -Force
}

Write-Host "Copying sample kubeconfig to $dest"
Copy-Item -Path $sample -Destination $dest -Force

# Run npm install in tools/kubec
Push-Location $scriptDir
if (Test-Path 'package.json') {
  Write-Host "Running npm install in $scriptDir"
  & npm install
} else {
  Write-Host "No package.json found in $scriptDir; skipping npm install"
}

if ($NpmLink) {
  Write-Host "Running npm link (may require permissions and will modify global npm links)"
  & npm link
}
Pop-Location

if ($AutoStartServer) {
  # Start server.js detached
  $nodeExe = 'node'
  $serverJs = Join-Path $scriptDir 'server.js'
  if (-not (Test-Path $serverJs)) { Write-Error "server.js not found at $serverJs"; exit 3 }
  Write-Host "Starting kubec dev server (detached)..."
  $startInfo = New-Object System.Diagnostics.ProcessStartInfo
  $startInfo.FileName = $nodeExe
  $startInfo.Arguments = "`"$serverJs`""
  $startInfo.WorkingDirectory = $scriptDir
  $startInfo.UseShellExecute = $true
  [System.Diagnostics.Process]::Start($startInfo) | Out-Null
  Write-Host "Server started. It will run detached. Visit http://localhost:51821 if running." 
}

Write-Host "Setup complete. If you want to remove the backup, inspect the .bak file created in $destDir."
Write-Host "To use the CLI now (if linked): kubec ctx"
