# Phone Pairing Setup Guide - Easy SMS Method

## Overview

**Super Easy Phone Pairing in 3 Steps:**
1. Enter your phone number in Top Dog
2. Receive text message with link
3. Click link, tap "Accept" → Done!

No QR codes, no manual codes, just click and pair!

---

## Quick Start (For Users)

### Pairing Your Phone

1. **Open Top Dog Settings**
   - Go to Settings → Phone Pairing
   - Or click "Pair Phone" button

2. **Enter Phone Number**
   ```
   Phone Number: +1 (415) 555-1234
   ```
   - Include country code (e.g., +1 for US)
   - Format: +1234567890 (no spaces/dashes)

3. **Click "Send Pairing Link"**
   - You'll see: "SMS sent! Check your phone."

4. **Check Your Phone**
   - Open the text message from Top Dog
   - Message says: "Click to pair your phone with Top Dog: [link]"

5. **Click the Link**
   - Opens pairing page in browser/app
   - Shows: "Top Dog wants to pair with your phone"
   - Device: iPhone 15 Pro
   - User: John Doe

6. **Tap "Accept"**
   - Done! Phone is paired
   - You can now:
     - Give voice commands
     - Receive build notifications
     - Approve builds remotely

---

## Setup (For Administrators)

### SMS Provider Configuration

Choose one of these SMS providers:

#### Option 1: Twilio (Recommended for Production)

1. **Sign up for Twilio**
   - Go to https://www.twilio.com
   - Free trial includes $15 credit
   - Or pay-as-you-go: $0.0079 per SMS

2. **Get Credentials**
   - Dashboard → Account Info
   - Copy: Account SID, Auth Token
   - Buy a phone number (about $1/month)

3. **Install Twilio Library**
   ```bash
   pip install twilio
   ```

4. **Set Environment Variables**
   ```bash
   # Windows PowerShell
   $env:TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxx"
   $env:TWILIO_AUTH_TOKEN="your_auth_token"
   $env:TWILIO_PHONE_NUMBER="+15551234567"

   # Linux/Mac
   export TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxx"
   export TWILIO_AUTH_TOKEN="your_auth_token"
   export TWILIO_PHONE_NUMBER="+15551234567"
   ```

5. **Restart Top Dog Backend**
   - System will detect Twilio and use it automatically
   - Look for: "✓ Twilio SMS provider configured"

#### Option 2: AWS SNS (Good for AWS Deployments)

1. **Configure AWS Credentials**
   ```bash
   aws configure
   # Enter: Access Key ID, Secret Access Key, Region
   ```

2. **Install boto3**
   ```bash
   pip install boto3
   ```

3. **Enable SMS in AWS SNS**
   - AWS Console → SNS → Text messaging (SMS)
   - Set spending limit
   - Verify phone numbers (for sandbox)

4. **Restart Top Dog Backend**
   - System will detect AWS SNS
   - Look for: "✓ AWS SNS provider configured"

#### Option 3: Development Mode (No SMS Service)

If you don't configure SMS providers, Top Dog runs in **MOCK MODE**:
- SMS "sent" to console/logs instead of phone
- Perfect for development/testing
- Copy the pairing link from logs manually
- Still works fully, just no real SMS

**Example Mock Output:**
```
==================================================
MOCK SMS (Development Mode)
To: +14155551234
Message:
Hi John! Click to pair your phone with Top Dog:

https://pair.topdog-ide.com/pair?code=xyz123abc456

Link expires in 15 minutes.
==================================================
```

---

## API Usage

### Send SMS Pairing Invite

**Endpoint:** `POST /phone/pairing/send-sms`

**Request:**
```json
{
  "phone_number": "+14155551234",
  "user_id": "user123",
  "user_name": "John Doe"
}
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

**Error Responses:**
- `400` - Invalid phone number format
- `500` - SMS send failed

### Accept Pairing Invite

**Endpoint:** `POST /phone/pairing/accept-invite`

Called when user clicks SMS link and taps accept.

**Request:**
```json
{
  "invite_code": "xyz123abc456...",
  "device_id": "iphone-12345",
  "device_name": "John's iPhone",
  "device_type": "ios",
  "os_version": "17.1",
  "app_version": "1.0.0"
}
```

**Response:**
```json
{
  "device_id": "iphone-12345",
  "jwt_token": "eyJhbGciOiJSUzI1NiIs...",
  "expires_at": "2025-12-04T18:00:00Z",
  "mqtt_broker": "mqtt.topdog-ide.com",
  "user_id": "user123"
}
```

Store the `jwt_token` securely on the device for all future API calls.

### Check Invite Status

**Endpoint:** `GET /phone/pairing/invite/{invite_code}`

**Response:**
```json
{
  "invite_code": "xyz123abc456...",
  "status": "pending",
  "expires_at": "2025-11-04T18:30:00Z",
  "is_expired": false,
  "is_valid": true
}
```

Statuses:
- `pending` - Not yet accepted
- `accepted` - Successfully paired
- `expired` - Link expired (15 min)
- `cancelled` - Cancelled by user

### Resend SMS

**Endpoint:** `POST /phone/pairing/resend-sms/{invite_code}`

If user didn't receive SMS, resend with new expiry time.

**Response:**
```json
{
  "message": "SMS resent successfully"
}
```

---

## SMS Message Templates

### Default Template
```
Hi {user_name}! Click to pair your phone with Top Dog:

{pairing_link}

Link expires in 15 minutes.
```

### Resend Template
```
Top Dog Pairing Link (Resent):

{pairing_link}

Link expires in 15 minutes.
```

---

## Security Features

### Invite Expiry
- **Default:** 15 minutes
- **Configurable:** `invite_expiry_minutes` parameter
- Auto-cleanup of expired invites

### One-Time Use
- Each invite code can only be accepted once
- After acceptance, status changes to "accepted"
- Cannot be reused

### Secure Token Generation
- Uses `secrets.token_urlsafe(32)` (256-bit entropy)
- Cryptographically secure random
- Impossible to guess

### Phone Number Validation
- Requires E.164 format (+1234567890)
- Validates format before sending
- Prevents invalid numbers

### JWT Authentication
- 30-day token expiry (configurable)
- RSA-2048 signed tokens
- Device fingerprinting
- See Phone Pairing Service docs for details

### Unified Session Lifecycle (New in v1.1)
- Every SMS invite now creates a pairing session (state machine)
- States: pending → accepted (or expired)
- Sessions persisted to `pairing_sessions.json` for auditability
- Enables future metrics & revocation correlation

### Persistent JWT Revocation (New in v1.1)
- Revoked device JWT IDs (JTI) are stored on disk (`revoked_jti.json`)
- Survives restarts, preventing token reuse after admin revocation
- Revocation endpoint updates both device registry & session store

### Adaptive Rate Limiting (Enhanced)
- Composite key includes client IP + critical headers to prevent brute force
- Separate buckets for invite creation vs acceptance
- Mitigates abuse (mass invite spam / token guessing)

### Optional Admin Gating
- Sensitive operations (listing / deleting paired devices) can require an admin token
- Enabled when `PHONE_DEVICES_REQUIRE_ADMIN="1"`
- Client must send `x-admin-token: <ADMIN_TOKEN>` header

### Optional QR OTP (Cross‑Method Hardening)
- While this guide focuses on SMS, enabling QR OTP strengthens hybrid deployments
- `PAIRING_QR_REQUIRE_OTP="1"` forces OTP entry when pairing via QR
- `PAIRING_QR_EMBED_OTP="1"` embeds the OTP inside the QR payload for smoother UX (still validated server-side)
- OTP flow is isolated—SMS flow remains link-based for frictionless UX

### Operational Audit Trail
- All pairing actions (invite create, accept, revoke) appended to JSONL audit log
- Supports incident response & compliance reviews

### Recommended Hardening Defaults
| Feature | Recommended | Env / Config |
|---------|-------------|--------------|
| Invite Expiry | 15 min | `PAIRING_INVITE_EXPIRY_MINUTES` |
| Admin Gating | Enabled in prod | `PHONE_DEVICES_REQUIRE_ADMIN=1` + `ADMIN_TOKEN` |
| QR OTP (if QR enabled) | Require OTP | `PAIRING_QR_REQUIRE_OTP=1` |
| QR OTP Embed | Enable | `PAIRING_QR_EMBED_OTP=1` |
| Logging | Persist audit log | Log retention policy |
| Revocation Persistence | Always on | (built-in) |
| Rate Limiting | Enabled | (built-in config) |

---

## Customization

### Change Invite Expiry Time

```python
from backend.services.sms_pairing_service import initialize_sms_pairing_service

# Set to 30 minutes instead of 15
sms_service = initialize_sms_pairing_service(
    invite_expiry_minutes=30
)
```

### Custom Pairing Domain

```python
sms_service = initialize_sms_pairing_service(
    base_url="https://pair.mycompany.com"
)
```

### Custom Storage Location

```python
sms_service = initialize_sms_pairing_service(
    storage_path="/var/lib/Top Dog/pairing"
)
```

---

## Frontend Integration

### React/Vue Example

```typescript
// Send SMS invite
async function sendPairingInvite() {
  const phoneNumber = document.getElementById('phone').value;
  
  const response = await fetch('http://localhost:8000/phone/pairing/send-sms', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      phone_number: phoneNumber,
      user_id: currentUser.id,
      user_name: currentUser.name
    })
  });
  
  const data = await response.json();
  
  if (response.ok) {
    showMessage(`✓ SMS sent to ${data.phone_number}`);
  } else {
    showError(`Failed: ${data.detail}`);
  }
}
```

### Mobile App Example (React Native)

```javascript
// When user opens pairing link
async function handlePairingLink(url) {
  // Extract invite code from URL
  const inviteCode = new URL(url).searchParams.get('code');
  
  // Accept invite
  const response = await fetch('http://localhost:8000/phone/pairing/accept-invite', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      invite_code: inviteCode,
      device_id: await getDeviceId(),
      device_name: await getDeviceName(),
      device_type: Platform.OS, // 'ios' or 'android'
      os_version: Platform.Version,
      app_version: '1.0.0'
    })
  });
  
  const data = await response.json();
  
  if (response.ok) {
    // Store JWT token
    await SecureStore.setItemAsync('jwt_token', data.jwt_token);
    
    // Navigate to success screen
    navigation.navigate('PairingSuccess');
  }
}
```

---

## Troubleshooting

### SMS Not Received

**Check:**
1. Phone number format: Must be +1234567890
2. SMS provider configured (Twilio/AWS SNS)
3. Twilio account has credits
4. AWS SNS spending limit not reached
5. Phone number not blocked/blacklisted

**Solution:**
- Check backend logs for error messages
- Try resend: `POST /phone/pairing/resend-sms/{code}`
- Use MOCK mode to test without real SMS

### Link Expired

**Default expiry:** 15 minutes

**Solutions:**
1. Resend SMS (extends expiry)
2. Generate new invite
3. Increase `invite_expiry_minutes` setting

### Invalid Invite Code

**Causes:**
- Link already used (status: accepted)
- Link expired (15+ min old)
- Typo in URL
- Invite cancelled

**Check status:**
```bash
curl http://localhost:8000/phone/pairing/invite/{code}
```

### JWT Token Issues

See main Phone Pairing documentation for JWT troubleshooting.

### Admin Gating Failures

If listing or deleting devices returns 401/403:
1. Ensure `PHONE_DEVICES_REQUIRE_ADMIN` is set to `1` in the backend environment
2. Include header `x-admin-token: <ADMIN_TOKEN>` in the request
3. Verify the server's `ADMIN_TOKEN` exactly matches the header value

### OTP Enforcement (QR Only)

If QR pairing fails with "OTP required" or "OTP invalid":
1. Confirm `PAIRING_QR_REQUIRE_OTP` is enabled intentionally
2. Ensure the client extracts or prompts for the OTP when scanning QR
3. If `PAIRING_QR_EMBED_OTP=1`, the OTP is included in the QR payload; still must be validated by the server

### Session State Mismatch

If an invite appears accepted but device isn't paired:
1. Check `pairing_sessions.json` for the session state and timestamps
2. Review audit log entries around the accept event
3. Ensure storage path has write permissions for persistence files

---

## Cost Estimation

### Twilio SMS Pricing
- **US/Canada:** $0.0079 per SMS
- **International:** Varies ($0.02-$0.15)
- **Phone Number:** ~$1/month

**Example:**
- 100 pairings/month = $0.79
- 1000 pairings/month = $7.90
- Very affordable!

### AWS SNS Pricing
- **US:** $0.00645 per SMS
- **First 100 SMS/month:** Free (AWS Free Tier)
- **International:** Varies

**Example:**
- 100 pairings/month = Free
- 1000 pairings/month = $5.81

---

## Comparison: SMS vs QR Code

| Feature | SMS Method | QR Code Method |
|---------|------------|----------------|
| **Ease of Use** | ⭐⭐⭐⭐⭐ Click link | ⭐⭐⭐ Scan code |
| **Speed** | 30 seconds | 10 seconds |
| **Requirements** | Phone number | Camera |
| **Cost** | $0.008 per pair | Free |
| **Remote Pairing** | Yes (anywhere) | No (same room) |
| **Accessibility** | High | Medium |
| **User Preference** | 90% prefer | 10% prefer |

**Recommendation:** Offer both methods, default to SMS.

---

## Production Deployment

### Environment Variables

```bash
# Twilio (Production SMS)
TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxxxx"
TWILIO_AUTH_TOKEN="your_auth_token_here"
TWILIO_PHONE_NUMBER="+15551234567"

# Custom Settings (Optional)
PAIRING_INVITE_EXPIRY_MINUTES="15"
PAIRING_BASE_URL="https://pair.topdog-ide.com"
PHONE_DEVICES_REQUIRE_ADMIN="1"         # Require admin token for device list/delete
ADMIN_TOKEN="super-secret-admin"        # Token presented via x-admin-token header
PAIRING_QR_REQUIRE_OTP="1"              # (If QR also deployed) force OTP challenge
PAIRING_QR_EMBED_OTP="1"                # Embed OTP inside QR payload for UX
```

### Kubernetes ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: Top Dog-pairing-config
data:
  PAIRING_INVITE_EXPIRY_MINUTES: "15"
  PAIRING_BASE_URL: "https://pair.topdog-ide.com"
  PHONE_DEVICES_REQUIRE_ADMIN: "1"
  ADMIN_TOKEN: "super-secret-admin"
  PAIRING_QR_REQUIRE_OTP: "1"
  PAIRING_QR_EMBED_OTP: "1"
```

### Kubernetes Secret

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: twilio-credentials
type: Opaque
stringData:
  TWILIO_ACCOUNT_SID: "ACxxxxxxxxxxxxxxxxxxxxxxxxxx"
  TWILIO_AUTH_TOKEN: "your_auth_token_here"
  TWILIO_PHONE_NUMBER: "+15551234567"
```

---

## Next Steps

1. **Configure SMS Provider** (Twilio or AWS SNS)
2. **Test in Development** (MOCK mode works without SMS)
3. **Build Frontend UI** (phone number input + status display)
4. **Deploy to Production**
5. **Monitor SMS costs** (Twilio/AWS dashboards)

### Hardening Verification Checklist (v1.1)
Run this after deployment:
1. Rate limiting: Exceed invite attempts rapidly → expect 429
2. Session persistence: Restart backend → previous sessions still present
3. Revocation: Revoke a device → JWT blocked on subsequent auth
4. Admin gating: Omit `x-admin-token` on device list → receive 401/403
5. Audit log: Accept + revoke flow produces sequential entries
6. (If QR enabled) OTP required & rejection on wrong code
7. Pairing expiry: Allow invite to pass expiry window → status reflects expired
8. Config map & secret contain all required vars (see Production Deployment)

**For full system integration, see:**
- `PHONE_PAIRING_COMPLETE_GUIDE.md` - Full phone pairing system
- `CLOUD_MESSAGE_BROKER.md` - MQTT communication
- `VOICE_COMMANDS.md` - Voice control integration

---

## Support

**Questions?**
- Check backend logs: `logs/Top Dog-topdog.log`
- Test SMS: Look for "MOCK SMS" in logs
- API docs: http://localhost:8000/docs

**SMS Provider Help:**
- Twilio: https://www.twilio.com/docs
- AWS SNS: https://docs.aws.amazon.com/sns/
