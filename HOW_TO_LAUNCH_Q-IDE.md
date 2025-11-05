# 🚀 Top Dog - Easy Launch Guide

## Where to Find Your Launch Button

Your Top Dog has **3 easy ways to launch**:

---

## Method 1: Rocket Launcher (⭐ EASIEST)

### File: `🚀_LAUNCH_Top Dog.bat` 

**Location:** `c:\Quellum-topdog-ide\🚀_LAUNCH_Top Dog.bat`

**How to use:**
1. Open `c:\Quellum-topdog-ide\` folder in Windows Explorer
2. Look for the file with the **🚀 rocket emoji** at the start
3. **Double-click it**
4. Two windows open automatically
5. Browser opens to Top Dog automatically

✅ **Easiest method - just double-click and go!**

---

## Method 2: Desktop Shortcut (⭐ RECOMMENDED)

### File: `CREATE_DESKTOP_SHORTCUT.bat`

**Location:** `c:\Quellum-topdog-ide\CREATE_DESKTOP_SHORTCUT.bat`

**First-time setup (1 minute):**
1. Open `c:\Quellum-topdog-ide\`
2. Find `CREATE_DESKTOP_SHORTCUT.bat`
3. Double-click it
4. Click OK when it says "Desktop shortcut created"

**Every day after:**
1. Look on your **Windows Desktop**
2. Find the **Top Dog icon** (blue gear/cube icon)
3. **Double-click it** - Top Dog launches!

✅ **Most convenient - icon on your desktop**

---

## Method 3: Classic Launcher

### File: `START.bat`

**Location:** `c:\Quellum-topdog-ide\START.bat`

**How to use:**
1. Open `c:\Quellum-topdog-ide\`
2. Find `START.bat`
3. Double-click it

This is the original launcher. Still works great!

---

## Quick Reference

| Method | File | Time | Convenience |
|--------|------|------|-------------|
| 🚀 Rocket | `🚀_LAUNCH_Top Dog.bat` | 2 seconds | ⭐⭐⭐⭐⭐ |
| 🖥️ Desktop Shortcut | First: `CREATE_DESKTOP_SHORTCUT.bat` | 1 minute setup | ⭐⭐⭐⭐⭐ |
| Original | `START.bat` | 3 seconds | ⭐⭐⭐ |

---

## What Happens When You Launch

```
Double-click launcher
        ↓
Backend starts (Python/FastAPI on port 8000)
        ↓
Frontend starts (React/Vite on port 1431)
        ↓
Browser opens automatically to http://localhost:1431
        ↓
🎉 Top Dog is running!
        ↓
Complete Setup Wizard
        ↓
Choose LLM Provider (OpenAI, Anthropic, Google, Mistral)
        ↓
Start building your app!
```

---

## How to Create Desktop Shortcut

**One-time setup (only need to do once):**

1. Open Windows Explorer
2. Navigate to `c:\Quellum-topdog-ide\`
3. Double-click `CREATE_DESKTOP_SHORTCUT.bat`
4. Click "OK" when you see the success message
5. Check your **Desktop** - you'll see a new **"Top Dog"** icon

**From then on:**
- Just double-click the **Top Dog** icon on your desktop to launch!

---

## File Locations Summary

```
Windows Desktop
└── Top Dog (shortcut) ← Double-click this after setup!

C:\Quellum-topdog-ide\
├── 🚀_LAUNCH_Top Dog.bat      ← Easiest (with rocket emoji!)
├── CREATE_DESKTOP_SHORTCUT.bat  ← Create desktop icon
├── START.bat                ← Original launcher
├── INSTALL.bat              ← Installation (first-time only)
└── [other files]
```

---

## Troubleshooting

**"I can't find the launch file"**
- Look for files ending in `.bat`
- Look for the **🚀 rocket emoji** in the filename
- It's in `c:\Quellum-topdog-ide\`

**"Desktop shortcut didn't work"**
- Run `CREATE_DESKTOP_SHORTCUT.bat` again
- Make sure you clicked "OK" on the popup

**"Launcher won't open"**
- Make sure Python 3.11+ and Node.js 18+ are installed
- Run `INSTALL.bat` first to install dependencies
- Check that ports 8000 and 1431 are not in use

**"Browser won't open"**
- Wait 5 seconds after launching
- Manually go to http://localhost:1431
- Check that frontend started in the window

---

## After Launch

### URLs to Access

| Service | URL | Purpose |
|---------|-----|---------|
| Top Dog App | http://localhost:1431 | Main UI - Start here! |
| API Docs | http://localhost:8000/docs | Backend API reference |
| Backend API | http://localhost:8000 | Direct API access |

---

## Pro Tips

✅ **Fastest way:** Create desktop shortcut → Double-click daily

✅ **No installation headache:** Just use the rocket launcher

✅ **Multiple instances:** Yes, you can run multiple Top Dog windows (each project separate)

✅ **Keep running:** You can keep Top Dog running in the background

✅ **Logs:** Check `logs/` folder for troubleshooting

---

## 🎉 You're All Set!

Choose your favorite launch method and start building:

- **Desktop icon?** Run `CREATE_DESKTOP_SHORTCUT.bat` once
- **Quick launch?** Double-click `🚀_LAUNCH_Top Dog.bat`
- **Either way:** You'll have Top Dog running in seconds!

**Questions?** Check `README_INSTALLATION.md` for more details.

**Ready?** Launch Top Dog now! 🚀
