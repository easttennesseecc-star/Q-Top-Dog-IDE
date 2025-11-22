# Secrets Management

This repository previously contained live secrets in `.env`. They have been sanitized.

## Never Commit Real Secrets
Add real values only in local (untracked) `.env` or inject via your deployment platform (Kubernetes secrets, GitHub Actions, Azure Key Vault, AWS Secrets Manager, GCP Secret Manager).

## Files
- `.env.template` — placeholder keys for development.
- (Optional) `local.env` — your personal overrides (add to .gitignore).

## Rotation Steps (IMMEDIATE)
1. Log into Stripe dashboard; rotate API keys (secret + publishable) and webhook secret.
2. In Google Cloud Console, rotate OAuth Client secret (create new; delete old if unused).
3. In GitHub OAuth app settings, create or set client/secret if using GitHub login.
4. Replace `SESSION_SECRET` with a strong random 64+ char value.
5. In all deployed environments, update secret stores and redeploy pods / processes.

## Environment Injection (Examples)
Kubernetes (manifest / Helm values):
```
env:
  - name: STRIPE_SECRET_KEY
    valueFrom:
      secretKeyRef:
        name: stripe-secrets
        key: secret_key
```
GitHub Actions:
```
env:
  STRIPE_SECRET_KEY: ${{ secrets.STRIPE_SECRET_KEY }}
```

## Adding a New Secret
1. Add placeholder to `.env.template`.
2. Add real value to your local `.env` (untracked) or secret manager.
3. Reference via environment variable in code.

## Auditing Repository History
Because the old keys were committed, run after sanitizing:
```
# Install git filter-repo if needed
pip install git-filter-repo

# Remove the .env from history (creates rewritten history; coordinate with team)
git filter-repo --path .env --invert-paths
```
Then force push (be cautious):
```
git push origin --force --tags
```
All collaborators must reset their clones.

## Secure Defaults
- Use `SECURE_COOKIES=true` in production.
- Only enable telemetry if compliant with policy.
- Keep AI budget variables low to prevent runaway cost.

## Checklist
[ ] Rotate all exposed keys
[ ] Rewrite git history (optional but recommended)
[ ] Configure secret manager
[ ] Remove local plaintext secrets from CI artifacts

---
If you need automated rotation scripts, create them under `secrets/automation/`.
