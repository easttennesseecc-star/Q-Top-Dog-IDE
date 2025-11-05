# Third‑Party Setup – Professional Integrations

This runbook standardizes provisioning and configuration.

## Stripe
- Products & prices: FREE, PRO, PRO‑PLUS, TEAMS (S/M/L), ENTERPRISE (Std/Prem/Ult)
- Webhooks: subscribe to checkout.session.completed, customer.subscription.updated, ...
- Keys: STRIPE_PUBLISHABLE_KEY (frontend), STRIPE_SECRET_KEY (backend)
- Test flow: create checkout, pay with test card, verify webhook updates app state

## OAuth Providers
- GitHub, Google, Microsoft: client ID/secret, redirect URIs to https://Top Dog.com/oauth/callback
- Scopes minimal; rotate secrets regularly

## Monitoring & Analytics
- Sentry (errors): DSN in backend/frontend; release tracking
- PostHog (product analytics): autocapture + consent controls
- Uptime: Better Stack or Pingdom; API and frontend checks

## Email & Notifications
- Resend/Sendgrid for transactional email; domain verification and DKIM set up
- Provider keys in secrets; test templates and delivery

## Storage & Media
- DigitalOcean Spaces (S3): bucket for media assets; restricted IAM; lifecycle policies

## Media Synthesis Providers
- DALL·E, Midjourney (via bridge), Runway: API keys per user (BYOK); secure storage and on-demand injection

## Security
- Principle of least privilege for all keys; rotation schedule; audit access monthly
