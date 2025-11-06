param(
  [string]$Namespace = "topdog",
  [string]$Service = "topdog-topdog",
  [int]$Port = 8000
)

Write-Host "Running in-cluster /health smoke test..." -ForegroundColor Cyan

$cmd = @(
  "kubectl", "run", "curl", "--rm", "-i", "--restart=Never",
  "--image=curlimages/curl:8.8.0", "-n", $Namespace, "--",
  "-sS", ("http://{0}:{1}/health" -f $Service, $Port)
)

& $cmd | Tee-Object -Variable output | Out-Null

if ($LASTEXITCODE -ne 0) {
  Write-Error "Smoke test failed to execute. Exit code: $LASTEXITCODE"
  exit 1
}

try {
  $json = $output | ConvertFrom-Json
  if ($json.status -eq "ok") {
    Write-Host "✅ /health returned OK" -ForegroundColor Green
    exit 0
  } else {
    Write-Error "Smoke test returned unexpected payload: $output"
    exit 2
  }
} catch {
  Write-Error "Smoke test output not JSON: $output"
  exit 3
}
