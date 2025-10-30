# ✅ PRE-INSTALLATION VERIFICATION CHECKLIST

## Files Ready?

Check that these files exist in your Q-IDE folder:

- [ ] **INSTALL_OLLAMA_AUTO.bat** (Windows batch launcher)
- [ ] **INSTALL_OLLAMA_AUTO.ps1** (PowerShell automation script)

If both exist, you're good to go! ✅

---

## System Requirements

### **Must Have:**
- [ ] Windows 10 or Windows 11
- [ ] Admin privileges on this computer
- [ ] ~5 GB free disk space
- [ ] Internet connection (for download)
- [ ] ~20 minutes of time

### **Should Have:**
- [ ] Modern browser (Chrome, Edge, Firefox)
- [ ] Q-IDE already open in browser tab
- [ ] Quiet time (let it run without interruption)

---

## Pre-Installation Checklist

### **Before You Start:**

**1. Internet Connection**
- [ ] Check you're connected to internet
- [ ] Speedtest (should be at least 5 Mbps download)
- Test: Open Google in browser

**2. Disk Space**
- [ ] Press **Windows Key + E** (File Explorer)
- [ ] Right-click your C: drive
- [ ] Choose **Properties**
- [ ] Check "Free space" shows at least 5 GB
- [ ] If less: Delete some files and try again

**3. Admin Rights**
- [ ] Do you have admin access on this computer?
- Test: Try to download a file and save to C:\Program Files

**4. Browser Ready**
- [ ] Is Q-IDE open in a browser tab?
- [ ] Keep that tab open during installation

**5. Close Programs**
- [ ] Close any large programs (Visual Studio, heavy games)
- [ ] Close web browsers except Q-IDE
- [ ] Close antivirus/Windows Defender is fine (don't worry)

---

## Installation Files Verified

### **INSTALL_OLLAMA_AUTO.bat**
```
Purpose:  Windows launcher script
Size:     ~10 KB (should be small)
Type:     Batch file (.bat)
Location: C:\Quellum-topdog-ide\
Ready:    ✅
```

**To verify it exists:**
1. Open File Explorer
2. Navigate to: C:\Quellum-topdog-ide\
3. Look for: **INSTALL_OLLAMA_AUTO.bat**
4. Should have icon: ⚙️ (gear icon)

### **INSTALL_OLLAMA_AUTO.ps1**
```
Purpose:  PowerShell automation script
Size:     ~15 KB (should be small)
Type:     PowerShell script (.ps1)
Location: C:\Quellum-topdog-ide\
Ready:    ✅
```

**To verify it exists:**
1. Open File Explorer
2. Navigate to: C:\Quellum-topdog-ide\
3. Look for: **INSTALL_OLLAMA_AUTO.ps1**
4. Should have icon: ◨ (PowerShell icon) or document icon

---

## What Gets Downloaded

During installation, these things will be downloaded:

### **Ollama Setup (~50 MB)**
- Installer for Ollama
- Downloaded from: https://ollama.ai/download/OllamaSetup.exe
- Time: ~2-3 minutes on 5 Mbps internet

### **llama2 Model (~4 GB)**
- AI model that runs locally
- Downloaded from: Ollama's server
- Time: ~5-15 minutes on 5 Mbps internet

**Total Data:** ~4 GB
**Total Time:** ~15-25 minutes

---

## What Gets Installed

These components will be installed on your computer:

### **1. Ollama Application**
- Location: `C:\Program Files\Ollama\`
- Purpose: Local AI model manager
- Memory: ~200 MB on disk
- Resource: Uses your GPU if available

### **2. llama2 Model**
- Location: `C:\Users\[YourUsername]\.ollama\models\`
- Purpose: The actual AI model you'll use
- Memory: ~4 GB on disk
- Resource: Uses your GPU when running

### **3. Ollama Service**
- Name: Ollama background service
- Purpose: Runs AI locally without opening windows
- Auto-start: Yes (starts with your computer)
- Memory: ~100-500 MB RAM when in use

---

## What DOESN'T Get Installed

These things are NOT installed (in case you were worried):

- ❌ No crypto miners
- ❌ No adware
- ❌ No tracking software
- ❌ No unwanted browser extensions
- ❌ No subscription requirements
- ❌ No data collection

All open-source, safe, and free!

---

## Permissions Needed

During installation, you will see:

### **Windows UAC Prompt** (appears once)
```
"Do you want to allow this app to make changes to your device?"
                [No]  [Yes]
```

**Click:** **[Yes]** to continue

This is needed to:
- Install Ollama to Program Files
- Create folders and shortcuts
- Set up the service

**Don't worry:** You're just giving permission to run an installer

---

## Ready to Install?

### **Final Checklist Before You Click:**

- [ ] Both files found: INSTALL_OLLAMA_AUTO.bat + .ps1
- [ ] At least 5 GB free disk space
- [ ] Internet connection working
- [ ] Q-IDE browser tab open
- [ ] All unnecessary programs closed
- [ ] You have 20+ minutes
- [ ] Read all the above ✅

---

## You're Ready!

### **Next Step: Installation**

When you're ready:

1. **Open File Explorer**
2. **Navigate to:** C:\Quellum-topdog-ide\
3. **Find:** INSTALL_OLLAMA_AUTO.bat
4. **Double-click it** ← This starts everything
5. **Click "Yes"** when Windows asks for admin
6. **Watch the progress** (don't close the window!)
7. **See "Installation Complete! 🎉"** when done

---

## During Installation

### **What You'll See:**

**Timeline:**
```
Time    What You'll See
────────────────────────────────────────────
0:00    Batch launcher starts
0:05    UAC prompt - click [Yes]
0:10    PowerShell window opens
0:30    "DOWNLOADING OLLAMA" message
2:30    "INSTALLING OLLAMA" message
7:30    "DOWNLOADING YOUR FIRST MODEL" message
        (Big download now - 4 GB, takes time)
22:30   "STARTING OLLAMA SERVICE" message
23:00   "INSTALLATION COMPLETE! 🎉"
        Script asks about Gemini (optional)
```

### **What NOT to Do:**
- ❌ Don't close the PowerShell window
- ❌ Don't restart your computer during download
- ❌ Don't run other installers
- ❌ Don't disconnect from internet

### **What You CAN Do:**
- ✅ Use other applications
- ✅ Check email
- ✅ Browse the web (keep Q-IDE tab open)
- ✅ Get coffee ☕

---

## After Installation

### **Immediately After:**
1. Read the completion summary in the installer
2. Decide if you want Gemini setup (optional)
3. Type Y or N and press Enter
4. Installer closes

### **Next - Verify in Q-IDE:**
1. Go to Q-IDE browser tab
2. Press F5 to refresh
3. Wait 3-5 seconds
4. Look for green box: "Auto-Selected Best Options"
5. You should see Ollama listed
6. Click checkbox to select it
7. Done! 🎉

---

## Troubleshooting Before You Start

### ❓ "Where do I find the installer files?"
**Location:** Look in: `C:\Quellum-topdog-ide\`

**Quick way:**
1. Press Windows Key + R
2. Type: `explorer C:\Quellum-topdog-ide\`
3. Press Enter
4. Find: INSTALL_OLLAMA_AUTO.bat

### ❓ "What if I don't have 5 GB free?"
**Solution:** You need it for the model. Free up space:
- Delete old Windows.old folder (if exists)
- Empty Recycle Bin
- Delete old downloads
- Then try again

### ❓ "What if I'm not admin?"
**Solution:** 
- Ask your IT person for admin access, OR
- Run on a different computer where you have admin
- The installer REQUIRES admin to work

### ❓ "What if my internet is slow?"
**Solution:**
- Connect to faster WiFi or wired internet
- Close other downloads
- Model will just take longer - that's OK
- Don't interrupt the process

---

## I'm Ready to Install!

✅ **You've verified everything**
✅ **System meets requirements**
✅ **Files are in place**

### **Now:**
1. Open File Explorer
2. Go to: C:\Quellum-topdog-ide\
3. Find: **INSTALL_OLLAMA_AUTO.bat**
4. **Double-click it**
5. **Click "Yes"** to admin prompt
6. **Wait** and watch the progress
7. **Celebrate** when you see "Installation Complete! 🎉"

---

## Questions?

Read these guides:
- **INSTALLER_OVERVIEW.md** ← How everything works
- **START_HERE_INSTALL_OLLAMA.md** ← Quick start guide
- **OLLAMA_SETUP_COMPLETE_GUIDE.md** ← Detailed walkthrough

---

## Let's Do This! 🚀

Everything is ready. The automation will handle everything else.

**Time to get AI in your Q-IDE!**

🎉 See you on the other side!

