# Top Dog Tier Features – CLARIFIED (API Keys vs BYOK LLM)

## The Distinction

### **Top Dog API Keys** (for calling YOUR API)
```
FREE:        1 key   (one integration point)
PRO:         5 keys  (multiple projects)
PRO-PLUS:    10 keys (advanced projects)
TEAMS:       ∞ keys  (team members each get keys)
ENTERPRISE:  ∞ keys  (unlimited integrations)
```

### **BYOK LLM Keys** (customers bring provider API keys: OpenAI/Anthropic/etc)
```
FREE:        BYOK enabled (basic providers)
PRO:         BYOK enabled
PRO-PLUS:    BYOK enabled (multi-provider + policies)
TEAMS:       BYOK enabled (team-wide key management)
ENTERPRISE:  BYOK enabled (+ data residency, on‑prem options)
```

Note: Q‑IDE does not ship a managed LLM by default. BYOK is the baseline for all tiers. For Enterprise, models are customer‑managed (BYOK and/or self‑hosted on the customer’s infrastructure). The platform does not operate models for Enterprise accounts.

---

## Updated Feature Matrix (BYOK enabled for all tiers)

### Core Execution
| Feature | FREE | PRO | PRO+ | TEAMS | ENTERPRISE |
|---------|------|-----|------|-------|------------|
| **API Calls/day** | 20 | 10K | 50K | 100K-∞ | Unlimited |
| **Code Execution** | | | | | |
| **LLM Requests/day** | 2 | 1K | 5K | 10K-∞ | Unlimited |
| **Storage** | 0.5GB | 100GB | 250GB | 1TB | 10TB+ |
| **Concurrent Jobs** | 1 | 5 | 8 | 10+ | 50+ |

### Developer Tools & API Access
| Feature | FREE | PRO | PRO+ | TEAMS | ENTERPRISE |
|---------|------|-----|------|-------|------------|
| **Top Dog API Keys** | 1 | 5 | 10 | ∞ | ∞ |
| **Webhooks** | | | | | |
| **Debug Logs Retention** | 7d | 30d | 60d | 90d | Forever |
| **Version Control** | | | | | |

### LLM Customization (BYOK is default across all tiers)
| Feature | FREE | PRO | PRO+ | TEAMS | ENTERPRISE |
|---------|------|-----|------|-------|------------|
| **Managed LLMs (platform keys)** | | | | | Optional add‑on |
| **BYOK LLM Support** | | | | | |
| **Supported Providers** | OpenAI (basic) | OpenAI, Anthropic | OpenAI, Anthropic, Cohere | All major | All + custom/privates |
| **Custom Integrations** | | Limited | | | |

### Collaboration
| Feature | FREE | PRO | PRO+ | TEAMS | ENTERPRISE |
|---------|------|-----|------|-------|------------|
| **Team Members** | 1 | 1 | 1 | 5-100 | ∞ |
| **Role-Based Access** | | | | | |
| **Shared Workspaces** | | | | | |
| **Audit Logs** | | | | | |
| **Resource Quotas** | | | | | |

### Compliance & Enterprise
| Feature | FREE | PRO | PRO+ | TEAMS | ENTERPRISE |
|---------|------|-----|------|-------|------------|
| **HIPAA Ready** | | | | | |
| **SOC2 Certified** | | | | | |
| **SSO/SAML** | | | | | Premium+ |
| **Data Residency** | | | | | Ultimate |
| **On-Premise Deploy** | | | | | Ultimate |

### Support
| Feature | FREE | PRO | PRO+ | TEAMS | ENTERPRISE |
|---------|------|-----|------|-------|------------|
| **Support** | Community | Email | Email | Phone+Email | 24/7 Phone |
| **Response Time** | 72hr | 24hr | 12hr | 4-24hr | 1hr |
| **Account Manager** | | | | | Premium+ |

---

## Database Schema Update

Add these columns to `membership_tiers` table:

```python
# Existing (stays the same)
api_keys_limit = 1  # Top Dog API keys

# NEW / Clarified – BYOK is baseline across all tiers
byok_llm_enabled = True             # All tiers support BYOK
byok_supported_providers = "openai" # Per tier: expand list (e.g., "openai,anthropic,cohere")

# Optional enterprise-only add-on for platform-managed keys
platform_managed_llm_enabled = False

# Example values per tier:
# FREE:        api_keys_limit=1,  byok_llm_enabled=True,  byok_supported_providers="openai"
# PRO:         api_keys_limit=5,  byok_llm_enabled=True,  byok_supported_providers="openai,anthropic"
# PRO-PLUS:    api_keys_limit=10, byok_llm_enabled=True,  byok_supported_providers="openai,anthropic,cohere"
# TEAMS-*:     api_keys_limit=-1, byok_llm_enabled=True,  byok_supported_providers="openai,anthropic,cohere,custom"
# ENTERPRISE:  api_keys_limit=-1, byok_llm_enabled=True,  byok_supported_providers="*", platform_managed_llm_enabled=True
```

---

## Implementation Notes

### BYOK (all tiers)

1. **User adds their provider API key(s)** → Stored encrypted or fetched on demand from a vault
2. **We don’t log secrets** → Forward securely to the provider
3. **Usage bills on the user’s provider account** → They pay OpenAI/Anthropic/etc directly
4. **We charge the Q‑IDE subscription** → Access to platform, gateway, safety, observability

### Security Best Practices:
- Never log API keys (not even truncated)
- Encrypt keys at rest with AES-256
- Use key rotation/versioning
- Audit log every key access
- Rate limit key API calls per tier

---

## Quick Summary (updated)

| What | Where | Who Pays |
|------|-------|----------|
| **Top Dog API Keys** | FREE–ENTERPRISE (1 to ∞) | User pays Q‑IDE subscription |
| **BYOK LLM Keys** | FREE–ENTERPRISE (baseline) | User pays OpenAI/Anthropic directly |
| **Platform‑managed LLMs** | Enterprise add‑on (optional) | Included in Enterprise add‑on or pass‑through |

So to answer your question: **BYOK is available on every tier (it’s the default)** — you’re providing the integration point; we don’t supply a managed LLM by default.

Want me to update the actual database schema to include the `byok_llm_enabled` column?

---

## BYOK and Regulated Segments (Operational Notes)

- Plan-aware and segment-aware SLAs: The backend exposes SLI metrics labeled with `plan` and `data_segment` (see `X-Plan` and `X-Data-Segment` headers). These labels enable Prometheus to evaluate tier/segment-specific alerts (e.g., stricter thresholds for `medical`/`scientific`).
- BYOK is baseline; discounting between BYOK vs platform‑managed is only relevant if you enable the Enterprise managed‑keys add‑on.
- Recommended headers for clients and gateways:
	- `X-Plan`: `Starter | Pro | Enterprise`
	- `X-Data-Segment`: `general | medical | scientific`
- Backend defaults (when headers are missing) are controlled via environment:
	- `DEFAULT_PLAN`, `DEFAULT_DATA_SEGMENT`, `DEFAULT_REGULATED_SEGMENT`, `ENABLE_REGULATED_DOMAINS`.

This approach keeps metering, SLAs, and pricing coherent without coupling billing logic into the runtime hot path.
