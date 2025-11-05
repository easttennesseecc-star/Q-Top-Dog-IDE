# 🚀 Rules Enforcement Quick Reference

## Access Rules UI
1. Open Top Dog: `http://127.0.0.1:1431`
2. Click **"Rules"** tab
3. Or press `Ctrl+Shift+P` → type "Rules Management"

## Quick Actions

### View All Rules
- Tab: "All Rules (13)"
- Shows: Active and inactive rules

### View Only Mandatory Rules
- Tab: "Mandatory (7)"
- Shows: Rules that block violations

### Create New Rule
```
1. Click "+ Create Rule" button
2. Fill form:
   - Name: Short descriptive name
   - Description: What the rule does
   - Rule Text: Detailed instructions (injected into prompts)
   - Type: code_style/architecture/security/etc.
   - Scope: global/project/file/build
   - Enforcement:
     🔴 mandatory = blocks violations
     🟠 strict = warns
     🟡 guidance = logs
     🟢 suggestion = informational
   - Priority: 1-100 (lower = higher priority)
   - Tags: comma-separated
3. Click "Create"
```

### Edit Rule
- Click ✏️ icon on rule card
- Modify fields
- Click "Update"

### View Rule Details
- Click 👁️ icon on rule card

### Delete Rule
- Click 🗑️ icon on rule card
- Confirm deletion

### Activate/Deactivate Rule
- Toggle switch on rule card
- Active = rule is enforced
- Inactive = rule is ignored

## API Quick Reference

### Base URL
```
http://127.0.0.1:8000/rules/
```

### List All Rules
```bash
curl http://127.0.0.1:8000/rules/
```

### Filter Rules
```bash
# Mandatory security rules only
curl "http://127.0.0.1:8000/rules/?rule_type=security&enforcement=mandatory"

# Active rules for a project
curl "http://127.0.0.1:8000/rules/?project_id=my-project&active_only=true"
```

### Create Rule
```bash
curl -X POST http://127.0.0.1:8000/rules/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Rule",
    "description": "Description",
    "rule_text": "Detailed instructions",
    "rule_type": "custom",
    "scope": "global",
    "enforcement": "strict",
    "priority": 50,
    "tags": ["tag1"]
  }'
```

### Update Rule
```bash
curl -X PATCH http://127.0.0.1:8000/rules/{rule_id} \
  -H "Content-Type: application/json" \
  -d '{"enforcement": "mandatory"}'
```

### Delete Rule
```bash
curl -X DELETE http://127.0.0.1:8000/rules/{rule_id}
```

### Activate Rule
```bash
curl -X POST http://127.0.0.1:8000/rules/{rule_id}/activate
```

### Deactivate Rule
```bash
curl -X POST http://127.0.0.1:8000/rules/{rule_id}/deactivate
```

### Preview Rules Injection
```bash
curl "http://127.0.0.1:8000/rules/preview/prompt?project_id=test&file_path=test.py"
```

## Default Rules Reference

### 🔴 MANDATORY (Blocks Violations)

| Priority | Name | Type | Tags |
|----------|------|------|------|
| 1 | No Hardcoded Credentials | security | security, credentials, critical |
| 1 | No Cross-Project Data Leakage | security | Top Dog, isolation, security |
| 2 | Validate User Input | security | security, validation, input |
| 2 | Pre-Build Approval Required | build | Top Dog, workflow, approval |
| 3 | Remember Build Context | architecture | Top Dog, context, ux |
| 5 | API Routes in Backend Only | architecture | api, security, backend |
| 10 | Use TypeScript for Frontend | code_style | typescript, frontend |

### 🟠 STRICT (Warns on Violations)

| Priority | Name | Type | Tags |
|----------|------|------|------|
| 15 | Separate Business Logic from UI | architecture | architecture, separation |
| 20 | Python Type Hints Required | code_style | python, type-hints |
| 25 | Avoid N+1 Queries | performance | performance, database |
| 30 | Write Tests for New Features | testing | testing, quality |

### 🟡 GUIDANCE (Best Practices)

| Priority | Name | Type | Tags |
|----------|------|------|------|
| 40 | Document Complex Functions | documentation | documentation, readability |
| 50 | Meaningful Variable Names | code_style | readability, naming |

## Rule Enforcement Levels

### 🔴 MANDATORY
- **Behavior**: Blocks responses that violate rule
- **Returns**: 400 error with violation details
- **Use for**: Critical security, architecture requirements
- **Example**: "Never hardcode credentials"

### 🟠 STRICT
- **Behavior**: Adds warning to response metadata
- **Returns**: 200 OK + `_rule_warnings` field
- **Use for**: Important code quality standards
- **Example**: "Use type hints"

### 🟡 GUIDANCE
- **Behavior**: Logs violation to audit trail
- **Returns**: 200 OK (no change to response)
- **Use for**: Best practices recommendations
- **Example**: "Document complex functions"

### 🟢 SUGGESTION
- **Behavior**: Informational only
- **Returns**: 200 OK (minimal logging)
- **Use for**: Nice-to-have preferences
- **Example**: "Use meaningful variable names"

## File Locations

### Rule Storage
```
~/.Top Dog/rules/
├── global_rules.json         # Global rules (all projects)
└── project_{id}_rules.json   # Project-specific rules
```

### Audit Logs
```
~/.Top Dog/logs/
└── rules_enforcement.jsonl   # Enforcement history
```

### Source Code
```
backend/
├── middleware/rules_enforcement.py
├── services/universal_rules_engine.py
├── routes/rules_api.py
└── scripts/setup_default_rules.py

frontend/
└── src/pages/RulesManagement.tsx
```

## Supported AI Models

All models automatically respect rules:

- ✅ Claude (3.5 Sonnet, 3 Sonnet, 3 Opus, 3.5 Haiku, 3 Haiku)
- ✅ OpenAI (GPT-4, GPT-4o, GPT-3.5-turbo)
- ✅ Google (Gemini Pro, Ultra, Flash)
- ✅ GitHub Copilot
- ✅ Cursor
- ✅ HuggingFace models
- ✅ Cohere models
- ✅ Stability AI
- ✅ Ollama (local models)
- ✅ Any model using standard LLM endpoints

## Troubleshooting

### Rules not enforcing?
```bash
# Check backend
curl http://127.0.0.1:8000/health

# List rules
curl http://127.0.0.1:8000/rules/

# Check specific rule is active
curl http://127.0.0.1:8000/rules/{rule_id}
```

### UI not loading?
1. Check backend: `http://127.0.0.1:8000/health`
2. Check frontend: `http://127.0.0.1:1431`
3. Open browser console (F12)
4. Check network tab for errors

### Rule violations not blocking?
- Verify rule enforcement is "mandatory"
- Check rule is active (toggle ON)
- Review audit logs: `~/.Top Dog/logs/rules_enforcement.jsonl`

## Key Benefits

✅ **Zero Configuration** - Works immediately after setup
✅ **All Models** - Claude, GPT-4, Gemini, Copilot, Cursor, etc.
✅ **Persistent** - Rules never forgotten
✅ **Flexible** - 4 enforcement levels
✅ **Auditable** - Complete enforcement history
✅ **User-Friendly** - Beautiful UI for non-technical users
✅ **API-First** - Full REST API for automation

## System Requirements Addressed

1. ✅ "courser doesnt respect user rules... not just courser all models"
2. ✅ "add build rules... like a digital qr code for identification"
3. ✅ "must address model forgetful ness"
4. ✅ "system must come up with an executeable plan for approval"
5. ✅ "super important no cross bleeding of information"

---

**Full Documentation**: See `RULES_ENFORCEMENT_SYSTEM_COMPLETE.md`

**Status**: ✅ PRODUCTION READY
