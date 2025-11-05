# Brand Sweep: Replace Q-IDE with Top Dog across all markdown files
# Preserves filenames and code examples while updating narrative text

Write-Host "Starting brand sweep..." -ForegroundColor Cyan
Write-Host ""

# Get all .md files
$files = Get-ChildItem -Path "c:\Quellum-topdog-ide" -Filter "*.md" -Recurse -File |
    Where-Object { $_.FullName -notlike "*\.archive\*" -and $_.FullName -notlike "*\node_modules\*" }

$totalFiles = $files.Count
$updatedFiles = 0

Write-Host "Found $totalFiles markdown files" -ForegroundColor Yellow
Write-Host ""

foreach ($file in $files) {
    Write-Host "Processing: $($file.Name)" -ForegroundColor Gray
    
    $content = Get-Content $file.FullName -Raw
    $original = $content
    
    # Simple pattern matching - replace Q-IDE and Q IDE with Top Dog
    $content = $content -replace 'Q-IDE\b', 'Top Dog'
    $content = $content -replace 'Q IDE\b', 'Top Dog'
    
    if ($content -ne $original) {
        Set-Content -Path $file.FullName -Value $content -NoNewline
        $updatedFiles++
        Write-Host "  Updated" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "Complete! Updated $updatedFiles of $totalFiles files" -ForegroundColor Green
