Deployment Domain, DNS, and Redirect Notes

Overview
- Primary host: https://topdog-ide.com
- Staging host: https://staging-app.topdog-ide.com
- API is path-routed on the same host(s); api subdomains are deprecated and 308-redirected.

DNS Records (Production)
- A/ALIAS/ANAME: topdog-ide.com → Ingress load balancer address
- CNAME: www.topdog-ide.com → topdog-ide.com
- (Optional legacy) CNAME: api.topdog-ide.com → topdog-ide.com (requests will be 308-redirected)

DNS Records (Staging)
- CNAME: staging-app.topdog-ide.com → staging ingress address
- (Optional legacy) CNAME: staging-api.topdog-ide.com → staging-app.topdog-ide.com (requests 308-redirected)

Ingress Configuration
- Production single-host ingress routes:
  - Backend: /api, /health, /metrics, /robots.txt, /sitemap.xml, /llm, /llm_auth, /consistency, /pfs, /verification, /assets, /build, /snapshots, /auth, /top-dog-ide, /q-ide
  - Frontend: /
- Staging mirrors the same pattern on https://staging-app.topdog-ide.com

api Subdomain Redirects (308 Permanent Redirect)
- Production: deploy/k8s/api-redirect-ingress.yaml redirects https://api.topdog-ide.com → https://topdog-ide.com$request_uri
- Staging: deploy/k8s/staging/api-redirect-ingress.yaml redirects https://staging-api.topdog-ide.com → https://staging-app.topdog-ide.com$request_uri

Backend Canonical Host Enforcement
- In app config (configmap), we set:
  - ENABLE_HOST_REDIRECT=true
  - CANONICAL_HOST=topdog-ide.com
  - ALTERNATE_HOSTS=www.topdog-ide.com
- Backend middleware honors these to canonicalize to the primary host.

CDN/WAF Considerations
- Single host simplifies TLS, CORS, session cookies, and OAuth callbacks.
- If CDN is used in front, forward /health and /metrics to origin without caching.
- Keep 308 redirects at the edge for api.* → single host to reduce round-trips.

Operational Steps
1) Ensure DNS records above are set.
2) Apply Kubernetes manifests (production):
   - kubectl apply -f deploy/k8s/configmap.yaml
   - kubectl apply -f deploy/k8s/backend-service.yaml
   - kubectl apply -f deploy/k8s/frontend-service.yaml
   - kubectl apply -f deploy/k8s/backend-deployment.yaml
   - kubectl apply -f deploy/k8s/frontend-deployment.yaml
   - kubectl apply -f deploy/k8s/api-redirect-ingress.yaml
   - kubectl apply -f deploy/k8s/ingress.yaml
3) Repeat for staging using files in deploy/k8s/staging/.
