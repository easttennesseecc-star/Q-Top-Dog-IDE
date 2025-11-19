Stripe configuration for CI/CD and cluster

Required secrets (create as Kubernetes secret 'stripe-keys' in target namespace):
- STRIPE_SECRET_KEY: Stripe API secret key
- STRIPE_PUBLIC_KEY: Stripe publishable key
- STRIPE_WEBHOOK_SECRET: Signing secret for webhooks
- STRIPE_PRICE_ID_PRO / STRIPE_PRICE_ID_PRO_ANNUAL
- STRIPE_PRICE_ID_PRO_PLUS / STRIPE_PRICE_ID_PRO_PLUS_ANNUAL
- STRIPE_PRICE_ID_TEAMS / STRIPE_PRICE_ID_TEAMS_ANNUAL
- STRIPE_PRICE_ID_ENTERPRISE / STRIPE_PRICE_ID_ENTERPRISE_ANNUAL

Create/update Kubernetes secret (example):

kubectl -n <namespace> delete secret stripe-keys --ignore-not-found=true
kubectl -n <namespace> create secret generic stripe-keys \
  --from-literal=STRIPE_SECRET_KEY=<sk_live_or_test> \
  --from-literal=STRIPE_PUBLIC_KEY=<pk_live_or_test> \
  --from-literal=STRIPE_WEBHOOK_SECRET=<whsec_...> \
  --from-literal=STRIPE_PRICE_ID_PRO=<price_...> \
  --from-literal=STRIPE_PRICE_ID_PRO_ANNUAL=<price_...> \
  --from-literal=STRIPE_PRICE_ID_PRO_PLUS=<price_...> \
  --from-literal=STRIPE_PRICE_ID_PRO_PLUS_ANNUAL=<price_...> \
  --from-literal=STRIPE_PRICE_ID_TEAMS=<price_...> \
  --from-literal=STRIPE_PRICE_ID_TEAMS_ANNUAL=<price_...> \
  --from-literal=STRIPE_PRICE_ID_ENTERPRISE=<price_...> \
  --from-literal=STRIPE_PRICE_ID_ENTERPRISE_ANNUAL=<price_...>

Notes:
- The deploy workflow now checks (non-blocking) for the presence of the 'stripe-keys' secret and prints a warning if missing.
- Provision Prices in Stripe dashboard for each tier (monthly + annual per Dev policy), then paste the IDs here.
- Ensure your webhook endpoint is configured and STRIPE_WEBHOOK_SECRET matches the deployed environment.
