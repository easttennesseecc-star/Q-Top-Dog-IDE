# 🎯 LLM Assignment UI - Quick Visual Guide

## The Problem We Solved

**Before:** Users said "there's no dropdown or visible buttons or way to change the LLM"
- The dropdown existed but was hidden in a form field
- No clear visual feedback showing which LLM was assigned
- Not obvious how to interact with role assignments

**After:** Clear, visible, interactive LLM assignment UI with:
- ✅ Prominent "Change LLM" buttons on each role card
- ✅ Hover dropdown menu showing all available models
- ✅ Visual badge showing currently assigned LLM
- ✅ One-click assignment with instant feedback
- ✅ Professional styling with smooth animations

---

## How to Assign an LLM to a Role

### Step 1: Go to LLM Setup Tab
Open the application and navigate to **LLM Setup** (Ctrl+Shift+P)

### Step 2: Click "Roles" Tab
Inside LLM Configuration, click the **Roles** tab to see all available roles:
- 🤖 **Analysis & Understanding** - Analyzes code, documents, and user intent
- 💻 **Coding** - Generates and optimizes code
- 🔍 **Code Review** - Reviews code quality and security
- 📝 **Documentation** - Writes clear, comprehensive documentation

### Step 3: Click "Change LLM" Button
Each role card now has a prominent blue **"Change LLM ▼"** button on the right side:

```
┌─────────────────────────────────────┐
│ 🤖 Analysis & Understanding         │  ← Role Name
│ Analyzes code, documents, and...    │  ← Description
│                        ┌──────────┐ │
│                        │Change LLM▼│ │  ← Click this!
│                        └──────────┘ │
└─────────────────────────────────────┘
```

### Step 4: Select Your LLM
When you hover over or click the "Change LLM" button, a dropdown menu appears:

```
┌──────────────────────┐
│ ✓ OpenAI (GPT-4) ☁️  │  ← Currently assigned (checkmark)
│   Google Gemini  ☁️  │
│   Claude         ☁️  │
│   Local Model    🖥️  │
│   Grok           ☁️  │
└──────────────────────┘
```

**Cloud providers (☁️)**: Use API keys you've configured
**Local models (🖥️)**: Run on your machine (Ollama, LLaMA, etc.)

### Step 5: See Instant Feedback
After clicking a model:
- The dropdown closes
- The green badge updates showing your new assignment
- The role immediately uses the selected LLM
- A success message appears at the top

```
✓ Analysis & Understanding now uses OpenAI (GPT-4)
```

---

## Visual Layout

### Role Assignment Card (New Design)

```
┌──────────────────────────────────────────────────────────────┐
│ 🤖 Analysis & Understanding          [✓ Claude 3]  [Change LLM▼] │
│                                                      [Unassign] │
│ Analyzes code, documents, and user intent                    │
│                                                                │
│ 💡 Recommended: Claude 3, GPT-4 Turbo                        │
└──────────────────────────────────────────────────────────────┘
```

**Left Side**: Role name, description, and recommendations
**Right Side**: 
- Green badge showing current assignment
- "Change LLM" dropdown button
- "Unassign" button (to remove the assignment)

---

## Key Features

### 1️⃣ Visual Feedback
- **Green badge** shows which LLM is currently assigned
- **Cloud/Local icons** (☁️/🖥️) show provider type at a glance
- **Color-coded buttons**: Cyan for assign, Red for unassign

### 2️⃣ Smart Dropdown
- **Hover-activated** - No need to click twice
- **Shows all providers** - See all options at once
- **Current selection highlighted** - Know what's assigned
- **Sorted by type** - Cloud providers first, then local

### 3️⃣ One-Click Assignment
- Click a model → Assignment happens instantly
- No confirmation dialogs needed
- Changes apply immediately
- Real-time feedback

### 4️⃣ Unassign Option
- If you want to remove an assignment, click "Unassign"
- Role reverts to "Not assigned" state
- Can be reassigned anytime

---

## Example Workflow

### Scenario: Setting up Q Assistant

**Goal**: Configure the "Coding" role to use OpenAI's GPT-4 Turbo

**Steps**:
1. Go to **LLM Setup** tab (Ctrl+Shift+P)
2. Go to **Authentication** tab → Add your OpenAI API key
3. Go to **Roles** tab
4. Find the **Coding** role card
5. Click the blue **"Change LLM ▼"** button
6. Select **OpenAI (GPT-4)** from the dropdown
7. ✓ Done! The role now uses GPT-4 for code generation

**Visual confirmation**: Green badge shows "✓ OpenAI (GPT-4)"

---

## Keyboard Navigation

While we recommend using the mouse for the visual dropdown, you can also:

1. **Tab** to the "Change LLM" button
2. **Enter** to focus the dropdown
3. **Arrow keys** to navigate menu items
4. **Enter** to select an LLM

---

## Troubleshooting

### Problem: "Change LLM" button is grayed out
**Solution**: First configure at least one LLM provider in the **Setup** or **Authentication** tab

### Problem: Dropdown doesn't appear when I hover
**Solution**: Click the button directly to open the dropdown

### Problem: Assignment didn't stick
**Solution**: The backend might not be running. Make sure:
- Backend server is running (`python main.py`)
- You see a success message before closing the tab

### Problem: No providers available
**Solution**: You haven't configured any LLMs yet:
1. Go to **Setup** tab
2. Select a provider (OpenAI, Google, etc.)
3. Paste your API key
4. Click "Save API Key"
5. Then come back to **Roles** to assign

---

## Technical Details

### API Endpoint Used
```
POST /llm_config/role_assignment
{
  "role": "coding",
  "model_name": "openai"
}
```

### Response
```json
{
  "success": true,
  "message": "Role assigned successfully!"
}
```

### File Locations
- **Configuration**: `~/.q-ide/llm_config.json`
- **Credentials**: `~/.q-ide/llm_credentials.json` (encrypted)
- **Component**: `frontend/src/components/LLMConfigPanel.tsx`

---

## What's Coming Next

### Planned Improvements
- 🔄 **Drag-and-drop** assignment interface
- 📊 **Model performance metrics** showing which LLM is fastest
- 🎚️ **Advanced settings** per role (temperature, max tokens, etc.)
- 🔐 **Credential manager** with secure storage indicators
- 📦 **Model library** showing what each LLM is best at

---

## Questions?

### Still can't find the dropdown?
1. Make sure you're on the **Roles** tab (not Providers or Setup)
2. Look for the blue **"Change LLM ▼"** button on the right side of each role card
3. Try clicking it directly if hovering doesn't work

### Want to try a different LLM?
1. Add another provider API key in the **Setup** tab
2. Return to **Roles** tab
3. Click "Change LLM" and select the new provider
4. Switch instantly - no restart needed!

### Having issues?
Check the browser console (F12) for error messages and report them so we can help!

---

## Summary

✅ **Simple**: Click → Select → Done
✅ **Visual**: See what's assigned with green badges
✅ **Fast**: One-click changes with instant feedback
✅ **Safe**: No accidental changes with clear UI
✅ **Powerful**: Switch between any configured LLM

**Welcome to professional LLM management!** 🚀
