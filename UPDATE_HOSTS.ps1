# Update Windows hosts file to resolve domain names to LoadBalancer IP
$hostsPath = "C:\Windows\System32\drivers\etc\hosts"

# Check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "❌ This script requires Administrator privileges!"
    Write-Host "Right-click the script and select 'Run with PowerShell as Administrator'"
    exit 1
}

# Backup the hosts file
$backup = "$hostsPath.backup_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
Copy-Item $hostsPath $backup
Write-Host "✅ Backup created: $backup"

# Read current hosts file
$hostContent = Get-Content $hostsPath -Raw

# Check if our entries already exist
if ($hostContent -contains "# Q-IDE Domain Names") {
    Write-Host "⚠️  Q-IDE entries already in hosts file. Skipping..."
} else {
    # Add new entries
    $newEntries = @"

# Q-IDE Domain Names (Added November 1, 2025)
134.199.134.151 q-ide.com
134.199.134.151 www.q-ide.com
134.199.134.151 api.q-ide.com
134.199.134.151 topdog.com
134.199.134.151 www.topdog.com
134.199.134.151 quellum.com
134.199.134.151 www.quellum.com
134.199.134.151 q
134.199.134.151 topdog
134.199.134.151 quellum
"@

    Add-Content -Path $hostsPath -Value $newEntries
    Write-Host "✅ Domain names added to hosts file:"
    Write-Host "   - q-ide.com, www.q-ide.com, api.q-ide.com"
    Write-Host "   - topdog.com, www.topdog.com"
    Write-Host "   - quellum.com, www.quellum.com"
    Write-Host "   - q, topdog, quellum (short names)"
}

Write-Host ""
Write-Host "✅ You can now access your site with any of these:"
Write-Host "   - http://q-ide.com"
Write-Host "   - http://topdog.com"
Write-Host "   - http://quellum.com"
Write-Host "   - http://q (short name)"
Write-Host "   - http://topdog (short name)"
Write-Host "   - http://quellum (short name)"
Write-Host ""
Write-Host "Press any key to close..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
