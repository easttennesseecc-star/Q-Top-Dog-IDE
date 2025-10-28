# 🚀 BUILD & LAUNCH QUICK CARD

## 1️⃣ CHECK PREREQUISITES (1 minute)

```powershell
node --version      # Should show v18+
pnpm --version      # Should show v8+
rustc --version     # Should show 1.70+
git --version       # Should show 2.x+
```

If any missing → Install from prerequisites section in WINDOWS_BUILD_GUIDE.md

---

## 2️⃣ BUILD (Choose one)

### Quick Build (5-10 min, ~150MB)
```powershell
cd C:\Quellum-topdog-ide
.\BUILD_WINDOWS.ps1
```

### Production Build ⭐ RECOMMENDED (15-25 min, ~80MB)
```powershell
cd C:\Quellum-topdog-ide
.\BUILD_WINDOWS.ps1 -Release
```

### Clean Production (20-30 min, full rebuild)
```powershell
cd C:\Quellum-topdog-ide
.\BUILD_WINDOWS.ps1 -Clean -Release
```

---

## 3️⃣ LOCATE MSI (30 seconds)

Build will show location at end, or open:
```powershell
explorer "C:\Quellum-topdog-ide\frontend\src-tauri\target\release\bundle\msi"
```

Look for: `Q-IDE_0.1.0_x64_en-US.msi`

---

## 4️⃣ INSTALL (1 minute)

```
Double-click MSI → Next → Install → Finish
```

Or PowerShell:
```powershell
Start-Process "Q-IDE_0.1.0_x64_en-US.msi"
```

---

## 5️⃣ LAUNCH (Anytime)

From Windows:
- Start Menu → Q-IDE → Click
- Desktop → Double-click Q-IDE shortcut

Or PowerShell:
```powershell
& "C:\Users\$env:USERNAME\AppData\Local\Programs\Q-IDE\Q-IDE.exe"
```

---

## ✅ VERIFY SUCCESS

After install:
- [ ] Application launched
- [ ] No error messages
- [ ] Can sign in with OAuth
- [ ] Can change background
- [ ] Can export/import settings
- [ ] Settings persist after restart

---

## 📤 DEPLOY (5 min)

### Option A: GitHub Releases
```powershell
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
# Upload MSI to release page
```

### Option B: Direct Link
```
1. Upload MSI to web server
2. Share link with users
3. Users download & install
```

### Option C: Network Share
```
1. Copy MSI to shared folder
2. Users access from network
3. Run installer
```

---

## 📚 FULL DOCUMENTATION

- **WINDOWS_DEPLOYMENT_READY.md** - Overview (start here)
- **WINDOWS_BUILD_GUIDE.md** - Detailed build instructions
- **WINDOWS_INSTALLATION_GUIDE.md** - User installation guide
- **BUILD_WINDOWS.ps1** - The build script (run this!)

---

## 🆘 QUICK TROUBLESHOOTING

**"Build won't start"**
```powershell
rustup update
.\BUILD_WINDOWS.ps1 -Clean -Release
```

**"Out of memory"**
- Close other apps
- Ensure 4GB+ RAM available

**"Installer won't run"**
```powershell
Start-Process "Q-IDE_0.1.0_x64_en-US.msi" -Verb RunAs
```

**"App won't launch after install"**
```powershell
# Uninstall:
msiexec /x "Q-IDE_0.1.0_x64_en-US.msi"

# Clean data:
Remove-Item "$env:LOCALAPPDATA\quellum" -Recurse -Force

# Reinstall:
Start-Process "Q-IDE_0.1.0_x64_en-US.msi"
```

See WINDOWS_BUILD_GUIDE.md for full troubleshooting.

---

## ⏱️ TIMELINE

| Step | Time | What to do |
|------|------|-----------|
| 1 | 1 min | Check prerequisites |
| 2 | 15-25 min | Build MSI |
| 3 | 1 min | Locate MSI file |
| 4 | 1 min | Install (double-click) |
| 5 | 1 min | Launch (Click Start Menu) |
| 6 | 2-5 min | Verify all works |
| 7 | 5 min | Deploy (upload to GitHub) |
| **TOTAL** | **~30-40 min** | **Ready to ship!** |

---

## 🎯 FINAL CHECKLIST

Before shipping to users:

- [ ] Build completed successfully
- [ ] MSI file exists and is ~80-100MB
- [ ] Installation tested on clean PC
- [ ] All features working
- [ ] Uninstall tested
- [ ] Release notes written
- [ ] MSI uploaded to release page
- [ ] Download link shared
- [ ] Users notified

---

## 🚀 YOU'RE READY!

```powershell
.\BUILD_WINDOWS.ps1 -Release
```

Then follow steps 3-7 above.

**Questions?** See full guide: WINDOWS_BUILD_GUIDE.md

---

**Built with ❤️ by Quellum Team - Q-IDE v0.1.0 - October 25, 2025**

