"""
Quick LLM Setup Guide - Shows you exactly how to get Gemini working with voice
"""

# SETUP GEMINI FOR Q ASSISTANT (With Voice Capabilities)

## Step 1: Get Your Gemini API Key
1. Go to: https://ai.google.dev
2. Click "Get API Key" 
3. Choose or create a Google Cloud project
4. Copy your API key

## Step 2: Configure Q-IDE to Use Gemini
### Option A: Using Environment Variable (Recommended)
```powershell
# Open PowerShell and run:
[Environment]::SetEnvironmentVariable("GOOGLE_API_KEY", "your_api_key_here", "User")

# Then restart Q-IDE:
# Close all windows and run LAUNCH_Q-IDE.bat again
```

### Option B: Using .env File
1. Create file: `c:\Quellum-topdog-ide\.env`
2. Add this line:
```
GOOGLE_API_KEY=your_api_key_here
```
3. Restart Q-IDE

## Step 3: Assign Gemini to Q Assistant
1. Open Q-IDE
2. Go to "LLM Setup" tab
3. Click "Providers" tab
4. Find "Google Gemini"
5. Click "Setup" if not configured, then add your API key
6. Go to "Roles" tab
7. Find "Q Assistant (Chat)" role
8. Click "Configure"
9. Select "Gemini Pro" from the dropdown
10. Click "Assign Model"

## Why Gemini for Q Assistant?
✅ Native voice synthesis (Web Speech API)
✅ Excellent conversation understanding
✅ Fast responses
✅ Free tier available
✅ Great for multi-turn dialogue

## Gemini Models Available:
- **gemini-1.5-pro** - Most capable (recommended)
- **gemini-1.5-flash** - Faster, cheaper
- **gemini-pro** - General purpose
- **gemini-pro-vision** - Can process images too

## After Setup:
1. Go back to chat
2. Q Assistant will now use Gemini
3. You can use voice input (Ctrl+M or click mic)
4. Gemini will respond with natural voice output

## Troubleshooting:
- **"API key not set"** → Restart Q-IDE after setting env var
- **"Gemini not working"** → Check your API key is correct at ai.google.dev
- **"No voice output"** → Browser needs permission for speaker (check browser settings)
- **"Can't select Gemini"** → First set your API key in the Providers tab

## Questions?
Ask Q Assistant directly in the chat! It can help with:
- Troubleshooting setup issues
- Understanding which model to use
- Creating your app with voice features
- Any other questions!
