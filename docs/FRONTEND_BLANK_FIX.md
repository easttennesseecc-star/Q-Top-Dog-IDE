# Frontend Blank Screen – Fix Guide

Goal: Resolve the SPA rendering blank despite HTTP 200 for `/`.

Most common causes
- Built with wrong backend URL (HTTPS vs HTTP or wrong host)
- Missing Vite env vars (VITE_* not baked into bundle)
- Base path misconfig (`base` in Vite config)
- Runtime JS error (silent) due to unavailable API or CORS

## Quick fix (bake correct API URL at build)

1) Ensure Vite uses a single env var, e.g. `VITE_API_BASE`.
2) Build with the correct value (temporary HTTP): `http://api.Top Dog.com`.
3) Rebuild and push a new image, then rollout.

Example Dockerfile (multi-stage; adjust paths):

```Dockerfile
# build stage
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
# Accept API base as build arg
ARG VITE_API_BASE
ENV VITE_API_BASE=${VITE_API_BASE}
RUN npm run build

# serve stage
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
# SPA fallback
RUN printf "server {\n  listen 3000;\n  server_name _;\n  root /usr/share/nginx/html;\n  location / {\n    try_files $uri /index.html;\n  }\n}\n" > /etc/nginx/conf.d/default.conf
EXPOSE 3000
CMD ["nginx","-g","daemon off;"]
```

Rollout hint (PowerShell):

```powershell
# build & push with correct API base
$tag = "ghcr.io/ORG/Top Dog-frontend:v1.0.1"
docker build . --build-arg VITE_API_BASE=http://api.Top Dog.com -t $tag ; docker push $tag
# patch deployment image
kubectl -n Top Dog set image deploy/frontend frontend=$tag
kubectl -n Top Dog rollout status deploy/frontend
```

## Robust fix (runtime env injection)

Baking env vars at build forces rebuilds for simple URL changes. Prefer runtime injection via `env.js` that the SPA reads at startup.

Pattern
- At container start, generate `/usr/share/nginx/html/env.js` from environment variables.
- `index.html` includes `<script src="/env.js"></script>` before the main bundle.
- App reads from `window.__ENV.API_BASE` with a small adapter.

Example entrypoint (sh):

```sh
cat > /usr/share/nginx/html/env.js <<EOF
window.__ENV = {
  API_BASE: "${API_BASE:-http://api.Top Dog.com}",
  FRONTEND_BASE: "${FRONTEND_BASE:-http://Top Dog.com}"
};
EOF
exec nginx -g 'daemon off;'
```

Vite adapter (ts):

```ts
// env.ts
export const API_BASE = (window as any).__ENV?.API_BASE || import.meta.env.VITE_API_BASE;
```

Kubernetes
- Mount a ConfigMap with `API_BASE` and `FRONTEND_BASE` into the frontend deployment env.
- Change container command to the entrypoint script above.

## Diagnostics
- Browser DevTools → Console: capture first error
- Network tab: confirm main JS bundle loads; check /env.js if using runtime pattern
- `kubectl logs deploy/frontend -n Top Dog` while refreshing
- `kubectl describe ingress Top Dog-ingress -n Top Dog` to confirm host rules
