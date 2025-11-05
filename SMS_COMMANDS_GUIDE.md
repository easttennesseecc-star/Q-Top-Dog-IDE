# 📱 SMS Commands - Send Ideas to Your IDE Anytime!

## Overview

**Suddenly remember something you need to add?** Just text it to your IDE!

No need to be at your computer. Send SMS messages from anywhere to:
- Add tasks to your todo list
- Save notes and ideas
- Set reminders
- Trigger builds
- Deploy to environments
- Check status

Your IDE processes the message and replies with confirmation.

---

## 🚀 How It Works

### Setup (One Time)

1. **Pair Your Phone** (see SMS_PAIRING_SETUP.md)
   - Enter your phone number in IDE
   - Receive text with pairing link
   - Click link → Done!

2. **Save the IDE Phone Number**
   - Your IDE has a dedicated phone number
   - Save it in your contacts as "Top Dog" or "Dev System"
   - Now you can text it anytime!

### Daily Use

Just text your IDE like you'd text a colleague:

```
"TODO: Fix the login bug"
"NOTE: Remember to update API docs"
"REMIND: Review Sarah's PR in 2 hours"
"BUILD ProjectAlpha"
"STATUS"
```

You'll get instant confirmation replies.

---

## 📝 Available Commands

### Add Tasks

**Format:** `TODO: <your task>`

**Examples:**
```
TODO: Fix bug in login page
TODO: Update README with new features
TODO: Review pull request #123
```

**Reply:**
```
✓ Added to your todo list:

"Fix bug in login page"

You now have 3 open tasks.
```

---

### Save Notes

**Format:** `NOTE: <your note>`

**Examples:**
```
NOTE: API key rotation scheduled for Friday
NOTE: Client wants dark mode in next release
NOTE: Performance improved by 40% after caching
```

**Reply:**
```
📝 Note saved:

"API key rotation scheduled for Friday"

You can access it in the IDE notes section.
```

---

### Set Reminders

**Format:** `REMIND: <what to remember>`

**Examples:**
```
REMIND: Check deployment logs in 1 hour
REMIND: Team standup at 10am tomorrow
REMIND: Database backup runs at midnight
```

**Reply:**
```
⏰ Reminder set:

"Check deployment logs in 1 hour"

I'll notify you when it's time.
```

---

### Trigger Builds

**Format:** `BUILD <project name>`

**Examples:**
```
BUILD ProjectAlpha
BUILD backend-api
BUILD staging
```

**Reply:**
```
🚀 Starting build for "ProjectAlpha"...

I'll notify you when it completes.
```

---

### Deploy

**Format:** `DEPLOY <environment>`

**Examples:**
```
DEPLOY staging
DEPLOY production
DEPLOY test
```

**Reply:**
```
🚀 Deploying to "staging"...

This may require approval. Check your notifications.
```

---

### Get Status

**Format:** `STATUS`

**Reply:**
```
📊 Status Report:

Tasks: 3 open
Notes: 8 saved
Reminders: 1 active

All systems operational ✓
```

---

### Get Help

**Format:** `HELP` or `?`

**Reply:**
```
📱 SMS Commands:

TODO: <task>
Add task to your list

NOTE: <text>
Save a note

REMIND: <what>
Set a reminder

BUILD <project>
Start a build

DEPLOY <env>
Deploy to environment

STATUS
Get current status

Reply with any command!
```

---

## 🎯 Smart Features

### Freeform Text

**Don't remember the command format?** No problem!

Just send natural text:

```
"Need to update the database schema"
```

The system will save it as a note and reply:

```
💬 Saved your message as a note:

"Need to update the database schema"

Reply HELP for command list.
```

### Multiple Commands

Send multiple commands in one message:

```
TODO: Fix bug
NOTE: Client approved the design
```

Each will be processed separately.

---

## 📞 Real-World Examples

### Morning Commute

```
You: "TODO: Review yesterday's build logs"
IDE: "✓ Added to your todo list..."

You: "STATUS"
IDE: "📊 Status Report: Tasks: 4 open..."
```

### Weekend Inspiration

```
You: "NOTE: Awesome idea - add AI code review bot"
IDE: "📝 Note saved..."
```

### Emergency Deployment

```
You: "DEPLOY hotfix-prod"
IDE: "🚀 Deploying to hotfix-prod... 
      This requires approval..."
```

### Quick Check

```
You: "STATUS"
IDE: "📊 All systems operational ✓"
```

---

## 🔒 Security

- **Phone Number Verification**: Only paired phones can send commands
- **User Authentication**: Each SMS is tied to your user account
- **Rate Limiting**: Protection against spam/abuse
- **Audit Trail**: All commands are logged
- **Sensitive Actions**: Builds/deploys may require additional approval

---

## 💡 Tips & Best Practices

1. **Save the IDE Number**
   - Add it to contacts for quick access
   - Use a memorable name like "Dev System"

2. **Use Clear Commands**
   - Start with the command keyword (TODO, NOTE, etc.)
   - Be specific and concise

3. **Check Your Messages**
   - The IDE replies to every command
   - Confirmation messages show what was saved

4. **View in IDE**
   - All SMS todos/notes sync to your IDE
   - Access them from the web interface

5. **Emergency Commands**
   - Text "CANCEL" to stop current operation
   - Text "STATUS" to check if system is responsive

---

## 🛠️ Technical Details

### SMS Providers Supported

- **Twilio** (recommended for production)
- **AWS SNS** (enterprise deployments)
- **Mock Mode** (development/testing)

### Webhook Endpoint

```
POST /phone/sms/webhook
```

Configure this URL in your SMS provider (Twilio/AWS SNS).

### Message Processing

1. SMS arrives at webhook
2. System identifies user by phone number
3. Message parsed using regex patterns
4. Command handler executes action
5. Confirmation sent back via SMS
6. Data synced to IDE

### Command Pattern Matching

```python
TODO: r'^todo:?\s*(.+)'
NOTE: r'^note:?\s*(.+)'
REMIND: r'^remind(?:er)?:?\s*(.+)'
BUILD: r'^build\s+(.+)'
DEPLOY: r'^deploy\s+(.+)'
STATUS: r'^status$'
```

Case-insensitive, flexible formatting.

---

## 📊 Data Storage

### In-Memory (Current)
- Todos, notes, reminders stored in service
- Persists for session duration

### Persistent Storage (Planned)
- SQLite database
- Synced with main IDE database
- Searchable and exportable

---

## 🔮 Future Enhancements

### Natural Language Processing
```
"remind me to check logs tomorrow morning"
→ Parses time: "tomorrow 9am"
```

### Voice-to-Text Integration
```
Voice message → Transcription → Command execution
```

### Smart Suggestions
```
Based on your patterns, the system suggests commands
```

### Team Sharing
```
Text "@team NOTE: Meeting moved to 3pm"
→ Shares note with entire team
```

### AI Enhancement
```
System uses Claude to understand complex requests
"Can you check if the staging build from yesterday failed?"
```

---

## 🆘 Troubleshooting

### "Message not processed"
- Check phone number is paired
- Verify SMS webhook is configured
- Check command format

### "No reply received"
- Verify IDE is running
- Check SMS provider status
- Test with "STATUS" command

### "Command not recognized"
- Reply with "HELP" to see available commands
- Use correct format (e.g., "TODO:" not "Todo")

### Rate Limit Errors
- Wait a few minutes
- Avoid sending too many messages quickly

---

## 📚 Related Documentation

- **SMS_PAIRING_SETUP.md** - How to pair your phone
- **PHONE_PAIRING_COMPLETE.md** - Complete system overview
- **API Documentation** - `/phone/sms/*` endpoints

---

## 🎉 Get Started!

1. **Pair your phone** (1 minute)
2. **Save the IDE number** to contacts
3. **Text "HELP"** to see commands
4. **Start sending ideas!**

**Never lose a great idea again!** 💡

---

*Last Updated: November 4, 2025*
*Top Dog Phone Integration v1.0*
