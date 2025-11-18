# Marketplace Quick Start (Windows)

This guide helps you start the API locally and run an end-to-end flow (register → login → list models → recommendations → chat) in one command. The product uses flat monthly plans with usage limits per tier; dev "funds" are optional for legacy/testing only.

## Prerequisites
- Windows PowerShell
- Python venv at `.venv` with dependencies installed (backend/requirements.txt)

```powershell
# From repo root
& .\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
```

## One-command quickstart

```powershell
# From repo root
scripts\quickstart.ps1 -Email you@example.com -UserPassword password123
```

- Starts uvicorn on http://127.0.0.1:8000 (or reuses a running one)
- Registers/logs in your user
- Shows your current tier and daily call limits via /api/tier/limits
- Lists models, fetches recommendations, sends a chat (enforced by tier-based limits)

Optional (legacy/dev only):

```powershell
scripts\quickstart.ps1 -Email you@example.com -UserPassword password123 -Funds 200
```

- Adds dev funds through the guarded /api/v1/auth/dev/add-funds endpoint (requires X-Dev-Funds-Key). This is not used for production enforcement.

Outputs include chosen model, response text, cost, and remaining API calls for today (based on your tier).

## Manual API usage
- Docs: http://127.0.0.1:8000/docs
- Health: `Invoke-RestMethod http://127.0.0.1:8000/health`

Auth
- POST /api/v1/auth/register
- POST /api/v1/auth/login
- GET  /api/v1/auth/me

Marketplace
- GET  /api/v1/marketplace/models
- POST /api/v1/marketplace/models/search
- POST /api/v1/marketplace/recommendations (Bearer token)
- POST /api/v1/marketplace/select-model (Bearer token)

Agent
- POST /api/v1/agent/chat (Bearer token)

Dev helper
- POST /api/v1/auth/dev/add-funds (Header: X-Dev-Funds-Key)
  - Body: { email?: string, user_id?: string, amount: number, txn_id?: string }

Tiers and limits
- GET  /api/tiers — public tier catalog (UI)
- GET  /api/tier/limits — authenticated per-user limits and today’s usage
