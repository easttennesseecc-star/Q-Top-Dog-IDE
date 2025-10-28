# 🏗️ Q-IDE Windows Build & Deployment Guide

## Overview

This guide covers everything needed to build, test, and deploy Q-IDE as a production-ready Windows MSI installer.

---

## 📋 Prerequisites

Before building, ensure you have:

### Required Software
- ✅ **Node.js 18+** - [Download](https://nodejs.org/)
- ✅ **pnpm 8+** - Install via: `npm install -g pnpm`
- ✅ **Rust 1.70+** - [Download](https://rustup.rs/)
- ✅ **Visual Studio Build Tools** - Required for Rust/Tauri on Windows
  - Download: [Visual Studio Community](https://visualstudio.microsoft.com/downloads/)
  - Install: "Desktop development with C++" workload
- ✅ **Git** - [Download](https://git-scm.com/)

### Windows Requirements
- **OS:** Windows 10 Build 19041 or later
- **RAM:** 4GB minimum (8GB recommended for smooth builds)
- **Disk:** 2GB free space
- **Administrator Access:** Required for build tools installation

### Quick Setup
```powershell
# 1. Install Rust (runs rustup installer)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# 2. Verify installation
node --version     # v18+
pnpm --version     # 8+
rustc --version    # 1.70+
cargo --version    # matches rustc

# 3. Clone repository
git clone https://github.com/quellum/q-ide.git
cd q-ide
```

---

## 🏗️ Building the MSI Installer

### Quick Build (Development)
```powershell
# From project root
.\BUILD_WINDOWS.ps1

# Output: frontend/src-tauri/target/debug/bundle/msi/Q-IDE_*.msi
# Time: ~5-10 minutes
# Size: ~150MB
```

### Production Build (Release)
```powershell
# Optimized for performance and size
.\BUILD_WINDOWS.ps1 -Release

# Output: frontend/src-tauri/target/release/bundle/msi/Q-IDE_*.msi
# Time: ~15-25 minutes (first time longer)
# Size: ~80-100MB (smaller, optimized)
```

### Clean Rebuild
```powershell
# Remove all previous builds and rebuild
.\BUILD_WINDOWS.ps1 -Clean -Release

# Time: ~20-30 minutes
# Useful if: Build fails, changing Rust dependencies, memory issues
```

### Manual Build Steps
```powershell
# If you prefer manual control:

# 1. Install dependencies
pnpm install

# 2. Build frontend
cd frontend
pnpm run build

# 3. Build Tauri (dev)
pnpm tauri build

# Or build Tauri (release)
pnpm tauri build --release

# 4. Find MSI
# Location: src-tauri/target/release/bundle/msi/Q-IDE_*.msi
```

---

## ✅ Testing Before Deployment

### Test the Built Installer

```powershell
# 1. Locate the MSI file
$msi = Get-ChildItem -Path "frontend/src-tauri/target/release/bundle/msi" -Filter "*.msi" | Select-Object -First 1

# 2. Test Installation (double-click or use msiexec)
Start-Process $msi.FullName

# 3. Follow installation wizard
# 4. Verify Q-IDE launches successfully
# 5. Test key features:
#    - Sign in with OAuth
#    - Change background
#    - Export/import settings
#    - Access build health monitor

# 6. Uninstall and test clean installation
# 7. Check Start Menu and Desktop shortcuts created
```

### Command-Line Testing
```powershell
# Quiet installation (no UI, for scripting)
msiexec /i "Q-IDE_0.1.0_x64_en-US.msi" /qb

# Verbose logging (troubleshooting)
msiexec /i "Q-IDE_0.1.0_x64_en-US.msi" /l*v install.log

# Uninstall
msiexec /x "Q-IDE_0.1.0_x64_en-US.msi" /qb

# Extract MSI contents (for inspection)
msiexec /a "Q-IDE_0.1.0_x64_en-US.msi" /qb TARGETDIR="C:\Temp\MSI_Extract"
```

### Feature Testing Checklist
- [ ] Application launches after installation
- [ ] Desktop shortcut works
- [ ] Start Menu entry appears
- [ ] Can uninstall from Control Panel
- [ ] Settings persist after restart
- [ ] No errors in Windows Event Viewer
- [ ] No temporary files left after uninstall

---

## 📦 Deployment Options

### Option 1: GitHub Releases (Recommended)
**Best for:** Public distribution, auto-updates

```powershell
# 1. Build release version
.\BUILD_WINDOWS.ps1 -Release

# 2. Create Git tag
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0

# 3. GitHub Actions automatically creates release

# 4. Upload MSI to release page
# 5. Users download from: https://github.com/quellum/q-ide/releases
```

### Option 2: Direct Download Link
**Best for:** Website distribution, enterprise

```powershell
# 1. Host MSI on web server
# 2. Create download link: https://downloads.q-ide.com/Q-IDE_0.1.0_x64.msi

# Users download and install locally
# Can use deployment scripts below
```

### Option 3: Enterprise Deployment
**Best for:** Corporate environments

```powershell
# Silent installation via Group Policy or deployment tools:

# Deploy via SCCM
$app = New-CMApplication -Name "Q-IDE 0.1.0"
$app.SetLocalProperty("DisplayName", "Q-IDE (TopDog)")

# Or via batch script
@echo off
msiexec /i \\fileserver\apps\Q-IDE_0.1.0_x64_en-US.msi /qb /norestart
echo Installation complete
```

---

## 🔐 Code Signing (Optional)

For production releases, code signing prevents Windows SmartScreen warnings:

```powershell
# 1. Obtain code signing certificate
# Cost: ~$100-500/year
# Providers: DigiCert, Sectigo, GlobalSign

# 2. Configure in tauri.conf.json
# Update: bundle.windows.certificateThumbprint

# 3. Update: bundle.windows.timestampUrl
# Example: "http://timestamp.digicert.com"

# 4. Rebuild with signing
.\BUILD_WINDOWS.ps1 -Release
```

---

## 🚀 Release Checklist

Before shipping to users:

### Pre-Release (1 week before)
- [ ] Update `frontend/package.json` version
- [ ] Update `frontend/src-tauri/tauri.conf.json` version
- [ ] Update `backend/package.json` version
- [ ] Update `README.md` with new version
- [ ] Test all features thoroughly
- [ ] Run E2E tests: `pnpm exec playwright test`
- [ ] Check for security issues: `npm audit`
- [ ] Document all changes in `CHANGELOG.md`

### Build Day
- [ ] Clean build: `.\BUILD_WINDOWS.ps1 -Clean -Release`
- [ ] Verify file size and integrity
- [ ] Test installer on clean Windows VM
- [ ] Create release notes (what's new, what's fixed)
- [ ] Generate SHA256 hash: `Get-FileHash "Q-IDE_*.msi"`

### Post-Release
- [ ] Upload MSI to GitHub Releases
- [ ] Upload to download server (if applicable)
- [ ] Update website with download link
- [ ] Announce on social media
- [ ] Notify existing users
- [ ] Monitor bug reports
- [ ] Plan next version (v0.1.1, etc.)

### Release Notes Template
```
## Q-IDE v0.1.0 - Production Release

### ✨ Features
- Background customization with gradients and particles
- OAuth authentication (Google, GitHub)
- Local data persistence with export/import
- Build health monitoring
- LLM integration framework

### 🐛 Bug Fixes
- Fixed Playwright E2E test selectors
- Improved error handling in image uploads
- Enhanced CSP security headers

### ⚙️ Improvements
- Optimized build size (now 80-100MB)
- Improved startup time
- Better error messages
- Cross-platform support ready

### 📋 System Requirements
- Windows 10 Build 19041+
- 2GB RAM minimum
- 200MB disk space

### 🔗 Links
- [Installation Guide](https://github.com/quellum/q-ide/blob/main/WINDOWS_INSTALLATION_GUIDE.md)
- [Full Documentation](https://github.com/quellum/q-ide/wiki)
- [Report a Bug](https://github.com/quellum/q-ide/issues)

### 🙏 Contributors
- Quellum Team
- Community contributors

---
**Download:** [Q-IDE_0.1.0_x64_en-US.msi](https://github.com/quellum/q-ide/releases/download/v0.1.0/Q-IDE_0.1.0_x64_en-US.msi)

**Hash:** SHA256: abc123def456...
```

---

## 🔧 Troubleshooting Build Issues

### Issue: "Rust not found"
```powershell
# Solution:
rustup update
cargo --version
# If still failing, reinstall Rust from https://rustup.rs/
```

### Issue: "Visual Studio Build Tools not found"
```powershell
# Solution:
# 1. Download Visual Studio Community
# 2. Install "Desktop development with C++"
# 3. Add to PATH if needed: $env:PATH += ";C:\Program Files\Microsoft Visual Studio\*"
```

### Issue: "pnpm install fails"
```powershell
# Solution:
pnpm store prune
pnpm install --force
# Or rebuild node_modules:
rm -r node_modules pnpm-lock.yaml
pnpm install
```

### Issue: "Build runs out of memory"
```powershell
# Solution - Reduce parallel builds:
$env:CARGO_BUILD_JOBS = "1"
.\BUILD_WINDOWS.ps1 -Release

# Or manually:
cd frontend
pnpm tauri build --release -- -j 1
```

### Issue: "MSI creation fails"
```powershell
# Check Tauri output for details:
pnpm tauri build --release 2>&1 | Tee-Object build-output.txt

# Common causes:
# 1. Icon files missing (check src-tauri/icons/)
# 2. Invalid version number (must be X.Y.Z)
# 3. Path length too long (move project to shorter path)
# 4. Windows certificate validation issues
```

### Issue: "Installer won't run on fresh Windows"
```powershell
# Possible cause: Missing VC++ redistributable
# Solution: Download and include:
# https://support.microsoft.com/en-us/help/2977003/

# Or require users to install first:
# https://aka.ms/vs/17/release/vc_redist.x64.exe
```

---

## 📊 Build Performance Tips

### Faster Builds
```powershell
# Use debug build (faster, larger):
.\BUILD_WINDOWS.ps1
# Time: 5-10 min, Size: 150-200MB

# Use sccache for caching:
cargo install sccache
$env:RUSTC_WRAPPER = "sccache"
```

### Faster Iterative Development
```powershell
# Run dev server without full rebuild:
cd frontend
pnpm run dev

# This runs Vite on localhost:1431 without Tauri wrapper
# Use when testing UI changes
```

### Disk Space Management
```powershell
# Release build is smaller but takes longer:
.\BUILD_WINDOWS.ps1 -Release

# Clean up old builds:
Remove-Item "frontend/src-tauri/target" -Recurse -Force
Remove-Item "frontend/dist" -Recurse -Force

# Cargo cache (1GB+):
cargo cache
```

---

## 🔄 Updating Installer for New Versions

### Version v0.1.0 → v0.2.0

```powershell
# 1. Update version numbers
# frontend/package.json: "version": "0.2.0"
# frontend/src-tauri/tauri.conf.json: "version": "0.2.0"
# backend/package.json: "version": "0.2.0"

# 2. Commit changes
git add .
git commit -m "chore: bump version to 0.2.0"

# 3. Create release tag
git tag -a v0.2.0 -m "Release v0.2.0"
git push origin main v0.2.0

# 4. GitHub Actions builds new MSI automatically
# 5. Download from: https://github.com/quellum/q-ide/releases/v0.2.0
```

### Backward Compatibility
- Previous version uninstalled automatically
- User settings preserved
- Can roll back if needed: Uninstall → Install previous version

---

## 📈 Monitoring & Analytics

### Track Installations
```powershell
# GitHub Release download counters:
# Shows automatically on release page

# Website analytics:
# Monitor clicks on download button
# Track geographic distribution
# Identify popular Windows versions
```

### Collect User Feedback
- Issue reporting link in app: Help → Report Bug
- GitHub Discussions for feature requests
- Email support for enterprise customers
- Usage analytics (optional, opt-in only)

---

## 🎯 Next Steps

1. **Build Release:** `.\BUILD_WINDOWS.ps1 -Release`
2. **Test Installer:** Double-click MSI, verify features
3. **Upload to GitHub:** Create release with MSI attachment
4. **Share Download:** Link in README, website, social media
5. **Monitor:** Watch for bug reports, gather feedback
6. **Plan v0.2.0:** Feature requests, improvements

---

## 📚 Additional Resources

- **Tauri Official Docs:** https://tauri.app/
- **Tauri Windows Bundler:** https://tauri.app/v1/guides/distribute/windows/
- **MSI Installer Docs:** https://docs.microsoft.com/en-us/windows/win32/msi/
- **Windows Code Signing:** https://docs.microsoft.com/en-us/windows/win32/appxpkg/how-to-sign-an-app-package/

---

## 💬 Support

Have questions? Check these first:
- See `WINDOWS_INSTALLATION_GUIDE.md` for user help
- See troubleshooting section above
- Open issue: https://github.com/quellum/q-ide/issues
- Email: support@q-ide.com

---

**Ready to build? Run:** `.\BUILD_WINDOWS.ps1 -Release` 🚀

