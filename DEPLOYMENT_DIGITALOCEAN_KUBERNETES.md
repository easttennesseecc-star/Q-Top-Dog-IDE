# DigitalOcean Deployment — Kubernetes (DOKS) Guide

This guide covers deploying Top Dog (Aura) to DigitalOcean Kubernetes (DOKS) with autoscaling and managed components. It assumes BYOK directory mode (no token resale) and the gateway/observability stack.

## Why Kubernetes for Top Dog?
- Horizontal scale: stateless API + web scale easily via HPA.
- Addons: managed Postgres (Cloud DB), managed object storage (Spaces), load balancers, cert-manager.
- Clear separation: IDE UI, API backend, gateway (NGINX/Envoy + OPA), observability (Prometheus/Grafana).

## Reference Architecture (DOKS)
- DOKS cluster: 3 nodes (e.g., s-2vcpu-4gb) with autoscaling up to 6–9 nodes.
- Ingress: NGINX Ingress Controller (managed LB), optional Envoy for ext_authz to OPA.
- OPA: sidecar or deployment for policy checks.
- Backend: FastAPI deployments with HPA (CPU 60–70% target) and readiness/liveness probes.
- Prometheus + Grafana: Helm charts; scrape gateway + backend; include alerts rules.
- Postgres: DigitalOcean Managed Database (Highly Available) for accounts/billing metadata.
- Object storage: DO Spaces for assets/logs if needed.

## Prerequisites
- DigitalOcean account and CLI (`doctl`).
- kubectl and Helm installed locally.
- Docker/registry (DigitalOcean Container Registry recommended).

## High-Level Steps
1) Create DOKS cluster
- Size: 3× s-2vcpu-4gb (or larger if needed). Enable autoscaling (min 3, max 9).
- Kubernetes version: current stable.

2) Set up Container Registry
- Create DO Container Registry; push images for backend and frontend.

3) Install NGINX Ingress Controller
- Use DO LB; annotate for HTTPS; attach domain.

4) Install cert-manager
- Issue Let’s Encrypt certificates (prod and staging issuers).

5) Deploy OPA and Envoy (optional ext_authz)
- Apply `envoy` Deployment + Service; mount OPA policy ConfigMaps.

6) Deploy Backend (FastAPI)
- Deployment with resource requests/limits and HPA (e.g., target CPU 60%).
- Service (ClusterIP) and Ingress routes.

7) Deploy Frontend (Aura Development)
- Static hosting (Spaces + CDN) OR pod-based (Nginx container). Ingress for app domain.

8) Observability
- Helm install kube-prometheus-stack; add scrape configs for gateway and backend; apply `observability/prometheus/alerts.yml` as a ConfigMap; reload Prometheus.

9) Managed Postgres
- Provision DO Managed PostgreSQL; configure secret for connection string; mount in backend.

10) Secrets and Config
- Use Kubernetes Secrets and ConfigMaps; avoid embedding secrets in images. BYOK keys stored per-tenant and not in code.

## Sample Manifests (skeleton)

Create a namespace:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: topdog
```

Backend Deployment:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: topdog-backend
  namespace: topdog
spec:
  replicas: 2
  selector:
    matchLabels: { app: topdog-backend }
  template:
    metadata:
      labels: { app: topdog-backend }
    spec:
      containers:
        - name: api
          image: <registry>/topdog-backend:latest
          ports: [{ containerPort: 8000 }]
          env:
            - name: MARKETPLACE_MODE
              value: "directory"
          readinessProbe:
            httpGet: { path: /healthz, port: 8000 }
            initialDelaySeconds: 5
          livenessProbe:
            httpGet: { path: /healthz, port: 8000 }
            initialDelaySeconds: 15
          resources:
            requests: { cpu: "100m", memory: "256Mi" }
            limits: { cpu: "500m", memory: "512Mi" }
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: topdog-backend-hpa
  namespace: topdog
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: topdog-backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 60
```

Service and Ingress (example):
```yaml
apiVersion: v1
kind: Service
metadata:
  name: topdog-backend-svc
  namespace: topdog
spec:
  type: ClusterIP
  selector: { app: topdog-backend }
  ports:
    - port: 80
      targetPort: 8000
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: topdog-app
  namespace: topdog
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
    - hosts: ["app.topdog.example.com"]
      secretName: topdog-tls
  rules:
    - host: app.topdog.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: topdog-backend-svc
                port: { number: 80 }
```

## Scaling Guidance
- Use HPA on backend; tune averageUtilization to keep CPU ~60–70% under load.
- Use Cluster Autoscaler on the node pool for burst traffic.
- Gateway and observability components can be given separate node pools if needed.

## Costs & Tradeoffs
- DOKS is a solid default for scale; Apps Platform (PaaS) is simpler but less flexible.
- For straightforward deployments, consider Apps Platform if you don’t need Envoy/OPA or custom observability.

## Next Steps
- Choose domain and DNS; configure Ingress + cert-manager.
- Push images to DOCR; deploy manifests above.
- Wire in `marketplace/LLM_DIRECTORY.json` into your front-end using `LLMDirectoryPanel`.
- If you prefer Terraform, scaffold DO cluster/node pool, DOCR, and Kubernetes add-ons via IaC.
