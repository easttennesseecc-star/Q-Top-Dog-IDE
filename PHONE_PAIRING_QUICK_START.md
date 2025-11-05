# Phone Pairing - Quick Start Guide

## For End Users: Pair Your Phone in 30 Seconds

### Step 1: Open Top Dog Settings
- Click the ⚙️ Settings icon
- Select "Phone Pairing" from menu

### Step 2: Enter Your Phone Number
```
Phone Number: +1 (555) 123-4567
              ↑
              Include country code!
```

### Step 3: Click "Send Pairing Link"
- You'll see: "✓ SMS sent to +15551234567"

### Step 4: Check Your Phone
- Open the text message from Top Dog
- Tap the link

### Step 5: Accept Pairing
- Review device info
- Tap "Accept" button
- Done! 🎉

### What You Can Do Now
- 🎤 **Voice Commands**: "Claude, run the build"
- 📲 **Get Notifications**: Build status, errors, approvals
- ✅ **Approve Builds**: Remotely approve deployments
- 🌍 **Works Anywhere**: From home, office, or anywhere!

---

## For Developers: Quick Setup

### 1. Install Dependencies
```bash
pip install twilio  # or: pip install boto3 for AWS SNS
```

### 2. Configure Twilio (5 minutes)
1. Sign up at https://www.twilio.com (free trial)
2. Get Account SID and Auth Token
3. Buy a phone number (~$1/month)

```bash
# Windows PowerShell
$env:TWILIO_ACCOUNT_SID="ACxxxxxxxxxx"
$env:TWILIO_AUTH_TOKEN="your_token"
$env:TWILIO_PHONE_NUMBER="+15551234567"

# Linux/Mac
export TWILIO_ACCOUNT_SID="ACxxxxxxxxxx"
export TWILIO_AUTH_TOKEN="your_token"
export TWILIO_PHONE_NUMBER="+15551234567"
```

### 3. Start Backend
```bash
cd backend
python main.py
```

Look for:
```
✓ Twilio SMS provider configured
✓ SMS Pairing Service initialized (expiry: 15min)
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### 4. Test SMS API
```bash
curl -X POST http://localhost:8000/phone/pairing/send-sms \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+14155551234",
    "user_id": "test-user",
    "user_name": "Test User"
  }'
```

**Response:**
```json
{
  "invite_code": "xyz123abc456...",
  "phone_number": "+14155551234",
  "expires_at": "2025-11-04T18:30:00Z",
  "status": "pending",
  "message": "SMS sent! Link expires in 15 minutes."
}
```

### 5. Check Your Phone
You should receive a text:
```
Hi Test User! Click to pair your phone with Top Dog:

https://pair.topdog-ide.com/pair?code=xyz123abc456...

Link expires in 15 minutes.
```

---

## Development Mode (No SMS Service)

Don't have Twilio setup yet? No problem!

### 1. Start Backend
```bash
cd backend
python main.py
```

You'll see:
```
⚠ No SMS providers configured - using MOCK mode
```

### 2. Send Test SMS
```bash
curl -X POST http://localhost:8000/phone/pairing/send-sms \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+14155551234",
    "user_id": "test-user"
  }'
```

### 3. Check Console
Backend logs will show:
```
==================================================
MOCK SMS (Development Mode)
To: +14155551234
Message:
Hi! Click to pair your phone with Top Dog:

https://pair.topdog-ide.com/pair?code=abc123xyz...

Link expires in 15 minutes.
==================================================
```

### 4. Copy the Link
- Copy the pairing URL from logs
- Paste in browser to test pairing flow
- Perfect for development!

---

## Common Issues

### "Invalid phone number format"
**Problem:** Phone number not in E.164 format  
**Solution:** Must start with + and include country code
```
❌ Wrong: 415-555-1234
❌ Wrong: (415) 555-1234
✅ Right: +14155551234
```

### "SMS not received"
**Check:**
1. Phone number correct?
2. Twilio configured? (Check env vars)
3. Twilio has credits?
4. Check backend logs for errors

**Quick test:**
```bash
curl http://localhost:8000/phone/health
# Should return: {"status": "ok"}
```

### "Link expired"
**Problem:** 15 minutes passed  
**Solution:** Resend SMS
```bash
curl -X POST http://localhost:8000/phone/pairing/resend-sms/{invite_code}
```

---

## Cost Calculator

### Twilio Pricing
- **SMS:** $0.0079 per message
- **Phone Number:** ~$1/month
- **No monthly minimums**

### Examples
```
10 pairings/month  = $0.08 + $1.00 = $1.08/month
100 pairings/month = $0.79 + $1.00 = $1.79/month
1000 pairings/month = $7.90 + $1.00 = $8.90/month
```

💡 **Tip:** One employee can pair multiple phones (work, personal, tablet)

---

## Next Steps

1. ✅ **SMS working?** Great! Now build the frontend UI
2. 📱 **Need mobile app?** See `MOBILE_APP_GUIDE.md`
3. 🎤 **Want voice commands?** See `VOICE_COMMANDS_GUIDE.md`
4. ☁️ **Deploy to production?** See `DEPLOYMENT_GUIDE.md`

---

## Support

**Documentation:**
- `PHONE_PAIRING_SMS_SETUP.md` - Detailed setup guide
- `PHONE_PAIRING_IMPLEMENTATION_SUMMARY.md` - What's been built
- `PHONE_PAIRING_VISUAL_DIAGRAMS.md` - Architecture diagrams

**API Docs:**
- http://localhost:8000/docs - Interactive API documentation

**Logs:**
- `logs/Top Dog-topdog.log` - Backend logs
- Look for "SMS" or "pairing" keywords

**Test Endpoints:**
- http://localhost:8000/phone/health - Health check
- http://localhost:8000/docs - API documentation

---

## FAQ

**Q: Can users pair multiple devices?**  
A: Yes! Each device gets its own JWT token. User can have iPhone, Android tablet, etc.

**Q: What if user changes phone number?**  
A: Just pair with new number. Old device auto-revokes when token expires (30 days).

**Q: Works internationally?**  
A: Yes! Twilio supports 180+ countries. Just use correct country code (+44 for UK, +49 for Germany, etc.)

**Q: Can I use my own SMS provider?**  
A: Yes! Extend `SMSPairingService` class and implement `_send_sms()` method.

**Q: Security concerns?**  
A: Multiple layers: One-time codes, 15-min expiry, JWT tokens, device fingerprinting, TLS encryption. See security docs.

**Q: Alternative to SMS?**  
A: Yes! QR code method still available. SMS is just the easier default option.

---

**Happy Pairing! 🚀📱**
