# Q-IDE Tier Features - CLARIFIED (API Keys vs BYOK LLM)

## 🔑 The Distinction

### **Q-IDE API Keys** (for calling YOUR API)
```
FREE:        1 key   (one integration point)
PRO:         5 keys  (multiple projects)
PRO-PLUS:    10 keys (advanced projects)
TEAMS:       ∞ keys  (team members each get keys)
ENTERPRISE:  ∞ keys  (unlimited integrations)
```

### **BYOK LLM Keys** (users bring their own from OpenAI/Anthropic/etc)
```
FREE:        ❌ No custom LLM support
PRO:         ❌ Only Q-IDE LLMs
PRO-PLUS:    ✅ BYOK enabled (can use own API keys)
TEAMS:       ✅ BYOK enabled (team admin manages keys)
ENTERPRISE:  ✅ BYOK enabled (+ data residency, on-premise)
```

---

## 📊 Updated Feature Matrix (with BYOK clarification)

### Core Execution
| Feature | FREE | PRO | PRO+ | TEAMS | ENTERPRISE |
|---------|------|-----|------|-------|------------|
| **API Calls/day** | 20 | 10K | 50K | 100K-∞ | Unlimited |
| **Code Execution** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **LLM Requests/day** | 2 | 1K | 5K | 10K-∞ | Unlimited |
| **Storage** | 0.5GB | 100GB | 250GB | 1TB | 10TB+ |
| **Concurrent Jobs** | 1 | 5 | 8 | 10+ | 50+ |

### Developer Tools & API Access
| Feature | FREE | PRO | PRO+ | TEAMS | ENTERPRISE |
|---------|------|-----|------|-------|------------|
| **Q-IDE API Keys** | 1 | 5 | 10 | ∞ | ∞ |
| **Webhooks** | ❌ | ✅ | ✅ | ✅ | ✅ |
| **Debug Logs Retention** | 7d | 30d | 60d | 90d | Forever |
| **Version Control** | ❌ | ✅ | ✅ | ✅ | ✅ |

### LLM Customization (BYOK)
| Feature | FREE | PRO | PRO+ | TEAMS | ENTERPRISE |
|---------|------|-----|------|-------|------------|
| **Q-IDE LLMs Only** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **BYOK LLM Support** | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Supported Providers** | - | - | OpenAI, Anthropic, Cohere | All | All |
| **Custom Integrations** | ❌ | ❌ | ✅ | ✅ | ✅ |

### Collaboration
| Feature | FREE | PRO | PRO+ | TEAMS | ENTERPRISE |
|---------|------|-----|------|-------|------------|
| **Team Members** | 1 | 1 | 1 | 5-100 | ∞ |
| **Role-Based Access** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Shared Workspaces** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Audit Logs** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **Resource Quotas** | ❌ | ❌ | ❌ | ✅ | ✅ |

### Compliance & Enterprise
| Feature | FREE | PRO | PRO+ | TEAMS | ENTERPRISE |
|---------|------|-----|------|-------|------------|
| **HIPAA Ready** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **SOC2 Certified** | ❌ | ❌ | ❌ | ❌ | ✅ |
| **SSO/SAML** | ❌ | ❌ | ❌ | ❌ | ✅ Premium+ |
| **Data Residency** | ❌ | ❌ | ❌ | ❌ | ✅ Ultimate |
| **On-Premise Deploy** | ❌ | ❌ | ❌ | ❌ | ✅ Ultimate |

### Support
| Feature | FREE | PRO | PRO+ | TEAMS | ENTERPRISE |
|---------|------|-----|------|-------|------------|
| **Support** | Community | Email | Email | Phone+Email | 24/7 Phone |
| **Response Time** | 72hr | 24hr | 12hr | 4-24hr | 1hr |
| **Account Manager** | ❌ | ❌ | ❌ | ❌ | ✅ Premium+ |

---

## 🎯 Database Schema Update

Add these columns to `membership_tiers` table:

```python
# Existing (stays the same)
api_keys_limit = 1  # Q-IDE API keys

# NEW - Add to schema
byok_llm_enabled = False       # Can user bring own LLM keys?
byok_supported_providers = ""  # "openai,anthropic,cohere" etc

# Example values per tier:
# FREE:        api_keys_limit=1,  byok_llm_enabled=False
# PRO:         api_keys_limit=5,  byok_llm_enabled=False
# PRO-PLUS:    api_keys_limit=10, byok_llm_enabled=True, supported="openai,anthropic,cohere"
# TEAMS-*:     api_keys_limit=-1, byok_llm_enabled=True, supported="openai,anthropic,cohere,custom"
# ENTERPRISE:  api_keys_limit=-1, byok_llm_enabled=True, supported="*"
```

---

## 💾 Implementation Notes

### For PRO-PLUS and above with BYOK:

1. **User adds their LLM API key** → Stored encrypted in database
2. **We never send the key to our servers** → Forward directly to provider
3. **Usage counts against THEIR account** → Not ours (they pay OpenAI directly)
4. **We charge the Q-IDE subscription** → For access to our platform

### Security Best Practices:
- ✅ Never log API keys (not even truncated)
- ✅ Encrypt keys at rest with AES-256
- ✅ Use key rotation/versioning
- ✅ Audit log every key access
- ✅ Rate limit key API calls per tier

---

## 🚀 Quick Summary

| What | Where | Who Pays |
|------|-------|----------|
| **Q-IDE API Keys** | FREE-ENTERPRISE (1 to ∞) | User pays Q-IDE subscription |
| **BYOK LLM Keys** | PRO-PLUS+ only | User pays OpenAI/Anthropic directly |
| **Q-IDE Managed LLMs** | FREE-ENTERPRISE | Included in subscription (usage limits apply) |

So to answer your question: **Yes, BYOK at PRO-PLUS means users bring their OWN OpenAI keys** - you're just providing the integration point, not supplying the keys.

Want me to update the actual database schema to include the `byok_llm_enabled` column?
