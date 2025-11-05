# Top Dog for Windows - Installation & Usage Guide

## 🚀 Quick Start (30 seconds)

### One-Click Installation
1. **Download** the latest `Q-IDE_*.msi` installer from [Releases](https://github.com/quellum/Top Dog/releases)
2. **Double-click** the MSI file
3. **Follow** the installation wizard
4. **Launch** Top Dog from your Start Menu or Desktop shortcut

That's it! ✅

---

## 📋 System Requirements

| Requirement | Minimum | Recommended |
|------------|---------|------------|
| **OS** | Windows 10 Build 19041+ | Windows 11 |
| **RAM** | 2 GB | 4+ GB |
| **Disk** | 200 MB | 500+ MB |
| **GPU** | Integrated | Dedicated (optional) |

---

## 💾 Installation Options

### Option 1: Installer (Recommended)
**Best for:** Most users

```powershell
# Double-click Q-IDE_0.1.0_x64_en-US.msi
# Windows will handle everything
```

**Includes:**
- ✅ Automatic Start Menu shortcut
- ✅ Desktop shortcut (optional)
- ✅ Uninstall option in Control Panel
- ✅ Automatic updates ready

### Option 2: Portable Version
**Best for:** USB drives, shared computers

```powershell
# Top Dog runs without installation
# Just run: Top Dog.exe
# No registry modifications
# No user data stored system-wide
```

### Option 3: Build from Source
**Best for:** Developers

```powershell
# From the project root:
.\BUILD_WINDOWS.ps1

# Or with full rebuild:
.\BUILD_WINDOWS.ps1 -Clean -Release

# Output: frontend/src-tauri/target/release/bundle/msi/
```

---

## 🎯 Features

### 🎨 Background Customization
- Gradient backgrounds with custom colors
- Particle effects (animated dots)
- Custom image backgrounds
- Real-time preview

### 🔐 Authentication
- Google OAuth sign-in
- GitHub OAuth sign-in
- Secure local storage

### 💾 Data Management
- Export settings to backup file
- Import settings from backup
- Local data persistence
- No cloud dependency

### 🏗️ Build Tools
- Build health monitoring
- Real-time status updates
- Environment variable support

### 🤖 AI Ready
- LLM integration framework
- Token pool management
- API client ready

---

## ⚙️ Configuration

### First Launch
1. Top Dog opens in ~/AppData/Local/quellum/Top Dog/
2. Local database created automatically
3. Settings stored locally (no cloud sync)

### Environment Variables
If you need custom configuration:

```powershell
# Create a .env file in the Top Dog data folder
# Default location: C:\Users\YourUsername\AppData\Local\quellum\Top Dog\

# Example .env:
BACKEND_URL=http://127.0.0.1:8000
LOG_LEVEL=debug
THEME=dark
```

### Data Location
```
C:\Users\YourUsername\AppData\Local\quellum\Top Dog\
├── app.db          # Local database
├── settings.json   # User settings
└── exports/        # Exported backups
```

---

## 🔧 Troubleshooting

### Top Dog Won't Start
```powershell
# Check if running:
Get-Process "Top Dog" -ErrorAction SilentlyContinue

# Kill process if stuck:
Stop-Process -Name "Top Dog" -Force -ErrorAction SilentlyContinue

# Restart:
# Use Start Menu shortcut
```

### Installer Won't Run
```powershell
# Try with admin privileges:
# Right-click MSI → Run as Administrator

# Or from PowerShell:
Start-Process "Q-IDE_0.1.0_x64_en-US.msi" -Verb RunAs
```

### Data Corruption
```powershell
# Export your settings before wiping:
# In Top Dog: Settings → Export Settings

# Clear local data:
Remove-Item "$env:LOCALAPPDATA\quellum\Top Dog\*" -Recurse -Force

# Restart Top Dog (fresh start)
```

### Performance Issues
```powershell
# Top Dog using too much memory?
# Check Settings → Performance → Clear Cache
# Restart application
```

---

## 🔄 Updates

### Checking for Updates
```
In Top Dog: Help → Check for Updates
```

### Manual Update
1. Visit [Releases](https://github.com/quellum/Top Dog/releases)
2. Download latest version
3. Run installer
4. Old version uninstalled automatically
5. Settings preserved

---

## 🗑️ Uninstallation

### Method 1: Control Panel (Recommended)
1. Open Windows Settings
2. Apps → Apps & Features
3. Find "Top Dog (TopDog)"
4. Click "Uninstall"
5. Follow the wizard

### Method 2: PowerShell
```powershell
# Uninstall via command line:
msiexec /x "{GUID}" /qb

# Or find GUID first:
Get-WmiObject Win32_Product | Where-Object {$_.Name -like "*Top Dog*"}
```

### What Gets Removed
- ✅ Top Dog executable and libraries
- ✅ Start Menu shortcuts
- ✅ Desktop shortcuts
- ❌ User settings (kept for reinstall)
- ❌ Exported backups (if any)

### Completely Remove All Data
```powershell
# After uninstalling, remove settings:
Remove-Item "$env:LOCALAPPDATA\quellum" -Recurse -Force
```

---

## 🐛 Bug Reports

Found an issue? Help us improve!

1. **Gather info:**
   ```powershell
   # Get system info:
   Get-ComputerInfo
   
   # Get Top Dog version:
   # In-app: Help → About
   ```

2. **Report on GitHub:**
   - https://github.com/quellum/Top Dog/issues
   - Include system info and steps to reproduce

3. **Include:**
   - Windows version (e.g., Windows 11 Build 22621)
   - Top Dog version (e.g., v0.1.0)
   - Error message (if any)
   - Steps to reproduce

---

## 📞 Support

| Channel | Contact |
|---------|---------|
| **Issues** | [GitHub Issues](https://github.com/quellum/Top Dog/issues) |
| **Discussions** | [GitHub Discussions](https://github.com/quellum/Top Dog/discussions) |
| **Email** | support@Top Dog.com |
| **Documentation** | [Wiki](https://github.com/quellum/Top Dog/wiki) |

---

## 🔒 Privacy & Security

### What Top Dog Collects
- ✅ Local settings (device only)
- ✅ Background preferences
- ✅ User authentication (OAuth tokens - encrypted locally)

### What Top Dog Does NOT Collect
- ❌ Personal data or browsing history
- ❌ System information without consent
- ❌ Analytics or telemetry (by default)
- ❌ IP address logs
- ❌ User activity tracking

### Permissions Required
- File system access (settings storage)
- Network access (OAuth, backend API)
- Display rendering (GPU acceleration, optional)

### Security Features
- 🔒 CSP (Content Security Policy)
- 🔒 HSTS (Secure transport)
- 🔒 X-Frame-Options (clickjacking protection)
- 🔒 Local storage encryption ready
- 🔒 OAuth 2.0 authentication

---

## 📚 Advanced Usage

### Command Line Arguments
```powershell
# Start Top Dog with debug logging:
Top Dog.exe --debug

# Start with custom data folder:
Top Dog.exe --data-dir="D:\MyData\Top Dog"

# Check version:
Top Dog.exe --version
```

### Portable Deployment
```powershell
# For shared networks or USB drives:
1. Extract Top Dog.exe to a folder
2. Copy to USB or network share
3. Run: .\Top Dog.exe
4. No installation needed

# Per-user settings stored in: .\AppData\
```

### Batch Installation (IT)
```powershell
# Install on multiple machines:
$computers = @("PC1", "PC2", "PC3")

foreach ($computer in $computers) {
    Invoke-Command -ComputerName $computer -ScriptBlock {
        Start-Process "\\fileserver\installers\Q-IDE_0.1.0_x64_en-US.msi" -Verb RunAs
    }
}
```

---

## 📖 Additional Resources

- **Getting Started:** See `QUICKSTART.md`
- **Feature Guide:** See `features/` folder in repo
- **API Reference:** See `docs/api/` in repo
- **Troubleshooting:** See `TROUBLESHOOTING.md`

---

## ✨ Version Information

- **Current Version:** v0.1.0
- **Release Date:** October 25, 2025
- **Build Status:** ✅ Production Ready
- **Last Updated:** October 25, 2025

---

**Enjoy Top Dog! 🚀**

Built with ❤️ by [Quellum Team](https://quellum.com)

