param(
  [string]$OutputDir = "${PWD}\exports"
)

function Get-BrowserPath {
  $candidates = @(
    # Edge
    "$Env:ProgramFiles(x86)\Microsoft\Edge\Application\msedge.exe",
    "$Env:ProgramFiles\Microsoft\Edge\Application\msedge.exe",
    # Chrome (system)
    "$Env:ProgramFiles\Google\Chrome\Application\chrome.exe",
    "$Env:ProgramFiles(x86)\Google\Chrome\Application\chrome.exe",
    # Chrome (per-user)
    "$Env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
  )
  foreach ($p in $candidates) {
    if (Test-Path $p) { return $p }
  }
  throw "No supported headless browser found (Edge or Chrome). Please install Edge or Chrome and rerun."
}

$ErrorActionPreference = 'Stop'
$browser = Get-BrowserPath
$root = Resolve-Path (Join-Path $PSScriptRoot "..")
$inDir = Join-Path $root "internal_docs\html"
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

function Export-HtmlToPdf([string]$htmlPath, [string]$pdfPath){
  $uri = (Resolve-Path $htmlPath).Path -replace "\\","/"
  $uri = "file:///" + $uri
  # Use Edge or Chrome headless depending on what's available
  if ($browser.ToLower().EndsWith("msedge.exe")) {
    & $browser --headless=new --disable-gpu --print-to-pdf="$pdfPath" "$uri" | Out-Null
  } else {
    & $browser --headless --disable-gpu --print-to-pdf="$pdfPath" "$uri" | Out-Null
  }
}

$docs = @(
  @{ in = "ONEPAGER_CUSTOMER_SAFE.html"; out = "TopDog-OnePager.pdf" },
  @{ in = "COMPARISON_CUSTOMER_SAFE.html"; out = "TopDog-Comparison.pdf" },
  @{ in = "NDA_DEEP_DIVE.html"; out = "TopDog-DeepDive-NDA.pdf" }
)

foreach($d in $docs){
  $inFile = Join-Path $inDir $d.in
  if(Test-Path $inFile){
    $outFile = Join-Path $OutputDir $d.out
    Write-Host "Exporting $($d.in) -> $outFile"
    Export-HtmlToPdf -htmlPath $inFile -pdfPath $outFile
  } else {
    Write-Warning "Missing $($d.in); skipping."
  }
}

Write-Host "Done. PDFs in: $OutputDir"
