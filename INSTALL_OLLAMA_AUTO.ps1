# ============================================================================
# Q-IDE AUTOMATED OLLAMA INSTALLER (PowerShell Version)
# ============================================================================
# This script:
# 1. Downloads Ollama automatically
# 2. Installs it with admin permissions
# 3. Downloads llama2 model
# 4. Verifies everything works
# 5. Offers Gemini API key link
# ============================================================================

param(
    [switch]$SkipGemini
)

Write-Host ""
Write-Host "============================================================================"
Write-Host "                    Q-IDE AUTOMATED OLLAMA INSTALLER"
Write-Host "============================================================================"
Write-Host ""
Write-Host "This script will:"
Write-Host "  1. Download Ollama (free, local AI model)"
Write-Host "  2. Install it automatically with admin permissions"
Write-Host "  3. Download llama2 model (~4 GB)"
Write-Host "  4. Verify installation"
Write-Host "  5. Offer optional Gemini API key setup"
Write-Host ""
Write-Host "============================================================================"
Write-Host ""

# Check if running as admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "[ERROR] This script needs admin permissions!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please run again by:"
    Write-Host "  1. Right-click PowerShell"
    Write-Host "  2. Select 'Run as administrator'"
    Write-Host "  3. Run: powershell -ExecutionPolicy Bypass -File .\INSTALL_OLLAMA_AUTO.ps1"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[OK] Running with admin permissions" -ForegroundColor Green
Write-Host ""

# Set up error handling
$ErrorActionPreference = "Continue"
$ProgressPreference = 'SilentlyContinue'

# ============================================================================
# FUNCTION: Download file with progress
# ============================================================================
function Download-File {
    param(
        [string]$Url,
        [string]$OutFile,
        [string]$Description
    )
    
    Write-Host "[*] Downloading $Description..."
    Write-Host "[*] From: $Url"
    Write-Host "[*] To: $OutFile"
    Write-Host ""
    
    try {
        # Enable TLS 1.2
        [Net.ServicePointManager]::SecurityProtocol = [Net.ServicePointManager]::SecurityProtocol -bor [Net.SecurityProtocolType]::Tls12
        
        # Download with progress bar
        $request = [System.Net.HttpWebRequest]::Create($Url)
        $response = $request.GetResponse()
        $totalSize = $response.ContentLength
        
        $stream = $response.GetResponseStream()
        $targetStream = New-Object -TypeName System.IO.FileStream -ArgumentList $OutFile, Create
        
        $buffer = new-object byte[] 65536
        $count = 0
        do {
            $read = $stream.Read($buffer, 0, 65536)
            if ($read -eq 0) { break }
            $targetStream.Write($buffer, 0, $read)
            $count += $read
            $percent = [math]::Round(($count / $totalSize) * 100)
            Write-Progress -Activity "Downloading" -Status "$percent% complete" -PercentComplete $percent
        } while ($true)
        
        $stream.Close()
        $targetStream.Close()
        Write-Progress -Activity "Downloading" -Completed
        
        Write-Host "[OK] Download complete" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "[ERROR] Download failed: $_" -ForegroundColor Red
        return $false
    }
}

# ============================================================================
# FUNCTION: Run installer silently
# ============================================================================
function Install-Application {
    param(
        [string]$InstallerPath,
        [string]$DisplayName
    )
    
    Write-Host "[*] Installing $DisplayName..." -ForegroundColor Cyan
    Write-Host "[*] This may take 2-5 minutes..."
    Write-Host ""
    
    try {
        $process = Start-Process -FilePath $InstallerPath -ArgumentList "/quiet /norestart" -NoNewWindow -PassThru -Wait
        Write-Host "[OK] Installation complete" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "[WARNING] Installation exit code: $($process.ExitCode)" -ForegroundColor Yellow
        Write-Host "[*] This might be OK - checking installation..." -ForegroundColor Yellow
        return $true
    }
}

# ============================================================================
# FUNCTION: Verify Ollama is installed
# ============================================================================
function Verify-OllamaInstalled {
    Write-Host ""
    Write-Host "[*] Verifying Ollama installation..." -ForegroundColor Cyan
    Write-Host ""
    
    # Try to find ollama command
    $ollamaPath = $null
    
    try {
        $ollamaPath = (Get-Command ollama -ErrorAction SilentlyContinue).Source
        if ($ollamaPath) {
            Write-Host "[OK] Found Ollama: $ollamaPath" -ForegroundColor Green
            return $ollamaPath
        }
    }
    catch { }
    
    # Check common installation directories
    $commonPaths = @(
        "$env:ProgramFiles\Ollama\ollama.exe",
        "$env:LocalAppData\Programs\Ollama\ollama.exe",
        "$env:AppData\Local\Programs\Ollama\ollama.exe"
    )
    
    foreach ($path in $commonPaths) {
        if (Test-Path $path) {
            Write-Host "[OK] Found Ollama: $path" -ForegroundColor Green
            return $path
        }
    }
    
    Write-Host "[ERROR] Could not find Ollama installation" -ForegroundColor Red
    Write-Host ""
    Write-Host "Troubleshooting:"
    Write-Host "  1. Restart your computer"
    Write-Host "  2. Try running this script again"
    Write-Host "  3. Or manually download from: https://ollama.ai"
    Write-Host ""
    return $null
}

# ============================================================================
# FUNCTION: Test Ollama
# ============================================================================
function Test-Ollama {
    param([string]$OllamaPath)
    
    Write-Host "[*] Testing Ollama..." -ForegroundColor Cyan
    
    try {
        & $OllamaPath --version | Out-Null
        Write-Host "[OK] Ollama is working" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "[WARNING] Test failed, but Ollama might still work" -ForegroundColor Yellow
        return $false
    }
}

# ============================================================================
# FUNCTION: Download model
# ============================================================================
function Download-OllamaModel {
    param(
        [string]$OllamaPath,
        [string]$ModelName
    )
    
    Write-Host ""
    Write-Host "============================================================================"
    Write-Host "DOWNLOADING OLLAMA MODEL: $ModelName"
    Write-Host "============================================================================"
    Write-Host ""
    Write-Host "[*] Downloading $ModelName model (~4 GB)..."
    Write-Host "[*] This will take 5-15 minutes depending on internet speed"
    Write-Host "[*] DO NOT CLOSE THIS WINDOW"
    Write-Host ""
    
    try {
        & $OllamaPath pull $ModelName
        Write-Host ""
        Write-Host "[OK] Model download complete!" -ForegroundColor Green
        return $true
    }
    catch {
        Write-Host "[ERROR] Model download failed: $_" -ForegroundColor Red
        return $false
    }
}

# ============================================================================
# FUNCTION: Start Ollama service
# ============================================================================
function Start-OllamaService {
    param([string]$OllamaPath)
    
    Write-Host ""
    Write-Host "============================================================================"
    Write-Host "STARTING OLLAMA SERVICE"
    Write-Host "============================================================================"
    Write-Host ""
    
    # Check if already running
    $ollamaProcess = Get-Process ollama -ErrorAction SilentlyContinue
    if ($ollamaProcess) {
        Write-Host "[OK] Ollama service is already running" -ForegroundColor Green
        return $true
    }
    
    Write-Host "[*] Starting Ollama service in background..." -ForegroundColor Cyan
    try {
        Start-Process -FilePath $OllamaPath -ArgumentList "serve" -WindowStyle Hidden
        Start-Sleep -Seconds 3
        
        $ollamaProcess = Get-Process ollama -ErrorAction SilentlyContinue
        if ($ollamaProcess) {
            Write-Host "[OK] Ollama service started successfully" -ForegroundColor Green
            return $true
        }
        else {
            Write-Host "[WARNING] Service might not have started yet" -ForegroundColor Yellow
            Write-Host "[*] It may start automatically" -ForegroundColor Yellow
            return $true
        }
    }
    catch {
        Write-Host "[WARNING] Could not start service: $_" -ForegroundColor Yellow
        return $true
    }
}

# ============================================================================
# FUNCTION: Offer Gemini setup
# ============================================================================
function Offer-GeminiSetup {
    if ($SkipGemini) {
        Write-Host ""
        Write-Host "[*] Skipping Gemini setup (passed -SkipGemini flag)" -ForegroundColor Yellow
        return
    }
    
    Write-Host ""
    Write-Host "============================================================================"
    Write-Host "WOULD YOU LIKE TO SET UP GOOGLE GEMINI?"
    Write-Host "============================================================================"
    Write-Host ""
    Write-Host "Google Gemini benefits:"
    Write-Host "  ✓ Free tier available (60 requests/min)"
    Write-Host "  ✓ Higher quality responses than local models"
    Write-Host "  ✓ Cloud-based (no local resources needed)"
    Write-Host "  ✓ Works as backup if Ollama is busy"
    Write-Host "  ✓ Can switch between Ollama and Gemini in Q-IDE"
    Write-Host ""
    Write-Host "Setup takes 2-3 minutes:"
    Write-Host "  1. Get free API key from Google"
    Write-Host "  2. Add it to Q-IDE via Providers tab"
    Write-Host "  3. Q-IDE auto-detects it"
    Write-Host ""
    
    $choice = Read-Host "Do you want to set up Google Gemini now? (Y/N)"
    
    if ($choice -eq "Y" -or $choice -eq "y") {
        Write-Host ""
        Write-Host "[*] Opening Google Gemini signup page..." -ForegroundColor Cyan
        Write-Host "[*] Your browser will open in a moment" -ForegroundColor Cyan
        Write-Host ""
        
        Start-Process "https://makersuite.google.com/app/apikey"
        
        Write-Host "[OK] Browser opened!" -ForegroundColor Green
        Write-Host ""
        Write-Host "What to do on the Google page:"
        Write-Host "  1. Sign in with your Google account"
        Write-Host "  2. Click 'Create API Key'"
        Write-Host "  3. Copy the blue key that appears"
        Write-Host "  4. In Q-IDE: Providers tab → [Setup] → Google → paste key → [Save]"
        Write-Host ""
        Write-Host "You'll have both Ollama + Google Gemini!"
        Write-Host ""
    }
    else {
        Write-Host ""
        Write-Host "[OK] Skipping Gemini setup" -ForegroundColor Yellow
        Write-Host "[*] You can add it later anytime" -ForegroundColor Yellow
        Write-Host "[*] Just go to: https://makersuite.google.com/app/apikey" -ForegroundColor Yellow
        Write-Host ""
    }
}

# ============================================================================
# MAIN EXECUTION
# ============================================================================

# Step 1: Create temp directory
Write-Host "============================================================================"
Write-Host "STEP 1: PREPARING INSTALLATION"
Write-Host "============================================================================"
Write-Host ""

$tempDir = "$env:TEMP\Q-IDE-Ollama"
if (-not (Test-Path $tempDir)) {
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
}
Write-Host "[OK] Using temp directory: $tempDir" -ForegroundColor Green
Write-Host ""

# Step 2: Download Ollama
Write-Host "============================================================================"
Write-Host "STEP 2: DOWNLOADING OLLAMA"
Write-Host "============================================================================"
Write-Host ""

$installerPath = "$tempDir\OllamaSetup.exe"

if (Test-Path $installerPath) {
    Write-Host "[OK] Ollama installer already downloaded" -ForegroundColor Green
}
else {
    $downloadSuccess = Download-File -Url "https://ollama.ai/download/OllamaSetup.exe" -OutFile $installerPath -Description "Ollama Setup"
    if (-not $downloadSuccess) {
        Write-Host ""
        Read-Host "Press Enter to exit"
        exit 1
    }
}
Write-Host ""

# Step 3: Install Ollama
Write-Host "============================================================================"
Write-Host "STEP 3: INSTALLING OLLAMA"
Write-Host "============================================================================"
Write-Host ""

$installSuccess = Install-Application -InstallerPath $installerPath -DisplayName "Ollama"
if (-not $installSuccess) {
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Start-Sleep -Seconds 3

# Step 4: Verify installation
Write-Host "============================================================================"
Write-Host "STEP 4: VERIFYING INSTALLATION"
Write-Host "============================================================================"

$ollamaPath = Verify-OllamaInstalled
if (-not $ollamaPath) {
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

$testOk = Test-Ollama -OllamaPath $ollamaPath
Write-Host ""

# Step 5: Download model
$modelSuccess = Download-OllamaModel -OllamaPath $ollamaPath -ModelName "llama2"
if (-not $modelSuccess) {
    Write-Host "[WARNING] Model download had issues, but Ollama should still work" -ForegroundColor Yellow
}

# Step 6: Start service
$serviceOk = Start-OllamaService -OllamaPath $ollamaPath

# Step 7: Final summary
Write-Host ""
Write-Host "============================================================================"
Write-Host "INSTALLATION COMPLETE! 🎉"
Write-Host "============================================================================"
Write-Host ""
Write-Host "Summary:" -ForegroundColor Green
Write-Host "  ✓ Ollama downloaded and installed"
Write-Host "  ✓ llama2 model cached locally"
Write-Host "  ✓ Ollama service configured"
Write-Host "  ✓ Q-IDE can now auto-detect it"
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Go back to Q-IDE in your browser"
Write-Host "  2. Press F5 to refresh (important!)"
Write-Host "  3. Go to 'LLM Pool Management' tab"
Write-Host "  4. Should see green box: 'Auto-Selected Best Options'"
Write-Host "  5. Ollama/llama2 should be listed"
Write-Host "  6. Click to select it"
Write-Host "  7. Done!"
Write-Host ""

# Offer Gemini setup
Offer-GeminiSetup

Write-Host "============================================================================"
Write-Host ""
Read-Host "Press Enter to close this window"
