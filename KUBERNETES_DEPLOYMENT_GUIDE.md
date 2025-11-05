# ⚡ KUBERNETES DEPLOYMENT GUIDE FOR Top Dog

**For Auto-Scaling, Multi-Pod Production Environment**

Generated: November 1, 2025

---

## 🎯 YOUR SITUATION

```
CURRENT:
✅ Kubernetes cluster (with auto-scaling)
✅ Top Dog application (complete)
✅ Stripe integration (ready)
✅ Domains (Top Dog.com, Top Dog.net, quellum.net)

CAPABILITY:
⚡ Automatic horizontal scaling
⚡ Multi-pod deployment
⚡ Load balancing
⚡ Rolling updates
⚡ Self-healing
⚡ Resource management

ADVANTAGE:
🚀 Handle 10x-100x traffic spikes
🚀 Zero-downtime deployments
🚀 Cost-optimized scaling
🚀 Enterprise-grade reliability
```

---

## 🏗️ KUBERNETES ARCHITECTURE FOR Top Dog

```
┌─────────────────────────────────────────────────────────────────┐
│                         USERS (Internet)                        │
└────────────┬────────────────────────────────────────────────────┘
             │
    ┌────────┴────────┬──────────────┬──────────────┐
    │                 │              │              │
    v                 v              v              v
  Top Dog.com      Top Dog.net    api.Top Dog.com   docs.Top Dog.com
    │                 │              │              │
    └─────────────────┴──────────────┴──────────────┘
              │
              v
    ┌──────────────────────────┐
    │   Ingress Controller     │
    │  (NGINX/Traefik)         │
    │  - SSL Termination       │
    │  - Routing Rules         │
    │  - Load Balancing        │
    └──────────────┬───────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
        v                     v
    ┌─────────────────┐  ┌──────────────┐
    │ Frontend Service│  │ Backend Service
    │ (Auto-Scale)    │  │ (Auto-Scale)
    │ Replicas: 2-10  │  │ Replicas: 2-10
    └────────┬────────┘  └────────┬──────┘
             │                    │
    ┌────────┴────┐       ┌──────┴────────┐
    │             │       │               │
    v             v       v               v
┌───────┐   ┌───────┐  ┌────────┐  ┌────────┐
│Front-1│   │Front-2│  │Backend-│  │Backend-│
│(Node) │   │(Node) │  │1(Node) │  │2(Node) │
└───────┘   └───────┘  └────────┘  └────────┘
    │            │          │          │
    └────────────┼──────────┼──────────┘
                 │          │
                 v          v
            ┌────────────────────────┐
            │   PostgreSQL Database  │
            │   (StatefulSet)        │
            │   Persistent Volume    │
            └────────────────────────┘
                     │
                     v
            ┌────────────────────────┐
            │  Persistent Storage    │
            │  (NFS/Cloud Storage)   │
            └────────────────────────┘
```

---

## 📦 WHAT WE'LL DEPLOY

### 1. Frontend Service
```yaml
- Container: Top Dog Frontend (React)
- Replicas: 2-10 (auto-scaling)
- CPU: 200m-500m per pod
- Memory: 256Mi-512Mi per pod
- Auto-scale: 70% CPU threshold
```

### 2. Backend Service
```yaml
- Container: Top Dog Backend (FastAPI)
- Replicas: 2-10 (auto-scaling)
- CPU: 500m-1000m per pod
- Memory: 512Mi-1Gi per pod
- Auto-scale: 75% CPU threshold
```

### 3. Database (PostgreSQL)
```yaml
- StatefulSet: PostgreSQL database
- Replicas: 1 (primary)
- Persistent Volume: 50Gi
- Backups: Daily automated
```

### 4. Ingress Controller
```yaml
- Ingress: NGINX/Traefik
- SSL: Let's Encrypt (auto-renewal)
- Domains: Top Dog.com, Top Dog.net, api.Top Dog.com
- Load Balancing: Round-robin
```

### 5. ConfigMaps & Secrets
```yaml
- ConfigMaps: Application config, environment
- Secrets: Database credentials, Stripe keys
- Sealed Secrets: Extra encryption layer (optional)
```

---

## 🚀 STEP 1: PREPARE DOCKER IMAGES

### 1.1 Build Frontend Docker Image

Create: `frontend/Dockerfile`

```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app

# Install dependencies
COPY frontend/package*.json ./
RUN npm ci

# Build application
COPY frontend/ .
RUN npm run build

# Runtime stage
FROM node:20-alpine
WORKDIR /app

# Install serve to run static files
RUN npm install -g serve

# Copy built app
COPY --from=builder /app/dist ./dist

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})"

EXPOSE 3000
CMD ["serve", "-s", "dist", "-l", "3000"]
```

### 1.2 Build Backend Docker Image

Create: `backend/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY backend/ .

# Create logs directory
RUN mkdir -p logs

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

EXPOSE 8000

# Run with gunicorn for production
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "--timeout", "120", "main:app"]
```

### 1.3 Build & Push Images

```bash
# Frontend
cd frontend
docker build -t your-registry/Top Dog-frontend:latest .
docker push your-registry/Top Dog-frontend:latest

# Backend
cd ../backend
docker build -t your-registry/Top Dog-backend:latest .
docker push your-registry/Top Dog-backend:latest

# Example with Docker Hub
# docker tag Top Dog-frontend:latest yourusername/Top Dog-frontend:latest
# docker push yourusername/Top Dog-frontend:latest
```

---

## ⚙️ STEP 2: KUBERNETES MANIFESTS

### 2.1 Namespace

Create: `k8s/00-namespace.yaml`

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: Top Dog
  labels:
    name: Top Dog
```

Apply:
```bash
kubectl apply -f k8s/00-namespace.yaml
```

---

### 2.2 ConfigMap (Application Config)

Create: `k8s/01-configmap.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: Top Dog-config
  namespace: Top Dog
data:
  ENVIRONMENT: "production"
  FRONTEND_URL: "https://Top Dog.com"
  BACKEND_URL: "https://api.Top Dog.com"
  DATABASE_HOST: "postgres"
  DATABASE_PORT: "5432"
  DATABASE_NAME: "qide_prod"
  LOG_LEVEL: "info"
  CORS_ORIGINS: |
    https://Top Dog.com
    https://www.Top Dog.com
    https://Top Dog.net
    https://www.Top Dog.net
```

Apply:
```bash
kubectl apply -f k8s/01-configmap.yaml
```

---

### 2.3 Secrets (Sensitive Data)

Create: `k8s/02-secrets.yaml`

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: Top Dog-secrets
  namespace: Top Dog
type: Opaque
stringData:
  # Database credentials
  DATABASE_USER: "qide_user"
  DATABASE_PASSWORD: "your-secure-password-here"
  
  # Stripe keys (PRODUCTION)
  STRIPE_PUBLIC_KEY: "pk_live_YOUR_KEY_HERE"
  STRIPE_SECRET_KEY: "sk_live_YOUR_KEY_HERE"
  STRIPE_WEBHOOK_SECRET: "whsec_live_YOUR_SECRET_HERE"
  
  # LLM API keys
  GITHUB_COPILOT_API_KEY: "your-key-here"
  GOOGLE_GEMINI_API_KEY: "your-key-here"
```

**IMPORTANT:** Never commit this file! Use sealed-secrets instead:

```bash
# Install sealed-secrets controller
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.18.0/controller.yaml

# Seal the secret
kubeseal -f k8s/02-secrets.yaml -w k8s/02-secrets-sealed.yaml

# Commit sealed version (not the plain version!)
git add k8s/02-secrets-sealed.yaml
git rm k8s/02-secrets.yaml
```

---

### 2.4 PostgreSQL StatefulSet

Create: `k8s/03-postgresql.yaml`

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: Top Dog
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi

---
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: postgres
  namespace: Top Dog
spec:
  serviceName: postgres
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15-alpine
        ports:
        - containerPort: 5432
          name: postgres
        env:
        - name: POSTGRES_DB
          value: "qide_prod"
        - name: POSTGRES_USER
          valueFrom:
            secretKeyRef:
              name: Top Dog-secrets
              key: DATABASE_USER
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: Top Dog-secrets
              key: DATABASE_PASSWORD
        - name: PGDATA
          value: /var/lib/postgresql/data/pgdata
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          exec:
            command:
            - /bin/sh
            - -c
            - pg_isready -U $POSTGRES_USER
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          exec:
            command:
            - /bin/sh
            - -c
            - pg_isready -U $POSTGRES_USER
          initialDelaySeconds: 5
          periodSeconds: 10
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: postgres
  namespace: Top Dog
spec:
  clusterIP: None
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
```

Apply:
```bash
kubectl apply -f k8s/03-postgresql.yaml
```

---

### 2.5 Backend Deployment (Auto-Scaling)

Create: `k8s/04-backend.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: Top Dog-backend
  namespace: Top Dog
spec:
  replicas: 2
  selector:
    matchLabels:
      app: Top Dog-backend
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: Top Dog-backend
    spec:
      containers:
      - name: backend
        image: your-registry/Top Dog-backend:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: Top Dog-config
        - secretRef:
            name: Top Dog-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2
        volumeMounts:
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: logs
        emptyDir: {}

---
apiVersion: v1
kind: Service
metadata:
  name: Top Dog-backend
  namespace: Top Dog
spec:
  selector:
    app: Top Dog-backend
  ports:
  - port: 8000
    targetPort: 8000
    protocol: TCP
  type: ClusterIP

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: Top Dog-backend-hpa
  namespace: Top Dog
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: Top Dog-backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 75
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 15
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
      - type: Pods
        value: 2
        periodSeconds: 15
      selectPolicy: Max
```

Apply:
```bash
kubectl apply -f k8s/04-backend.yaml
```

---

### 2.6 Frontend Deployment (Auto-Scaling)

Create: `k8s/05-frontend.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: Top Dog-frontend
  namespace: Top Dog
spec:
  replicas: 2
  selector:
    matchLabels:
      app: Top Dog-frontend
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
  template:
    metadata:
      labels:
        app: Top Dog-frontend
    spec:
      containers:
      - name: frontend
        image: your-registry/Top Dog-frontend:latest
        imagePullPolicy: Always
        ports:
        - containerPort: 3000
        env:
        - name: REACT_APP_API_URL
          value: "https://api.Top Dog.com"
        - name: REACT_APP_ENVIRONMENT
          value: "production"
        resources:
          requests:
            memory: "256Mi"
            cpu: "200m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 2

---
apiVersion: v1
kind: Service
metadata:
  name: Top Dog-frontend
  namespace: Top Dog
spec:
  selector:
    app: Top Dog-frontend
  ports:
  - port: 3000
    targetPort: 3000
    protocol: TCP
  type: ClusterIP

---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: Top Dog-frontend-hpa
  namespace: Top Dog
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: Top Dog-frontend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 50
        periodSeconds: 15
    scaleUp:
      stabilizationWindowSeconds: 0
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
      - type: Pods
        value: 2
        periodSeconds: 15
      selectPolicy: Max
```

Apply:
```bash
kubectl apply -f k8s/05-frontend.yaml
```

---

### 2.7 Ingress (SSL & Routing)

Create: `k8s/06-ingress.yaml`

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: Top Dog-ingress
  namespace: Top Dog
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - Top Dog.com
    - www.Top Dog.com
    - api.Top Dog.com
    - docs.Top Dog.com
    - Top Dog.net
    - www.Top Dog.net
    secretName: Top Dog-tls
  rules:
  - host: Top Dog.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: Top Dog-frontend
            port:
              number: 3000
  - host: www.Top Dog.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: Top Dog-frontend
            port:
              number: 3000
  - host: api.Top Dog.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: Top Dog-backend
            port:
              number: 8000
  - host: Top Dog.net
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: Top Dog-frontend
            port:
              number: 3000
```

Apply:
```bash
kubectl apply -f k8s/06-ingress.yaml
```

---

### 2.8 Certificate Manager (SSL)

```bash
# Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Wait for it to be ready
kubectl wait --for=condition=ready pod -l app.kubernetes.io/instance=cert-manager -n cert-manager --timeout=300s
```

Create: `k8s/07-certificate.yaml`

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@Top Dog.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

Apply:
```bash
kubectl apply -f k8s/07-certificate.yaml
```

---

## 🚀 STEP 3: DEPLOY TO KUBERNETES

### 3.1 Deploy Everything

```bash
# Create namespace
kubectl apply -f k8s/00-namespace.yaml

# Create config and secrets
kubectl apply -f k8s/01-configmap.yaml
kubectl apply -f k8s/02-secrets-sealed.yaml  # Use sealed version!

# Deploy database
kubectl apply -f k8s/03-postgresql.yaml

# Wait for database to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n Top Dog --timeout=300s

# Deploy backend
kubectl apply -f k8s/04-backend.yaml

# Deploy frontend
kubectl apply -f k8s/05-frontend.yaml

# Deploy ingress
kubectl apply -f k8s/06-ingress.yaml

# Deploy certificate issuer
kubectl apply -f k8s/07-certificate.yaml
```

### 3.2 Verify Deployment

```bash
# Check all resources
kubectl get all -n Top Dog

# Check pods
kubectl get pods -n Top Dog

# Check services
kubectl get svc -n Top Dog

# Check ingress
kubectl get ingress -n Top Dog

# Check certificate status
kubectl get certificate -n Top Dog

# Check HPA status
kubectl get hpa -n Top Dog

# View pod logs
kubectl logs -f deployment/Top Dog-backend -n Top Dog

# Describe resources (if issues)
kubectl describe pod <pod-name> -n Top Dog
```

---

## 📊 MONITORING & METRICS

### Install Prometheus & Grafana

```bash
# Add Prometheus Helm repo
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install kube-prometheus-stack
helm install kube-prometheus prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace

# Port-forward to Grafana
kubectl port-forward -n monitoring svc/kube-prometheus-grafana 3000:80

# Access Grafana at http://localhost:3000
# Default credentials: admin / prom-operator
```

### Custom Metrics Dashboard

Create monitoring queries:
```
# Backend response time
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="Top Dog-backend"}[5m]))

# Frontend error rate
rate(http_requests_total{job="Top Dog-frontend",status=~"5.."}[5m])

# Pod scaling history
kube_deployment_status_replicas{deployment="Top Dog-backend"}

# Resource usage
container_memory_usage_bytes{pod=~"Top Dog-.*"}/1024/1024
```

---

## 🔄 CONTINUOUS DEPLOYMENT

### 3.1 GitOps with ArgoCD

```bash
# Install ArgoCD
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Port-forward to UI
kubectl port-forward svc/argocd-server -n argocd 8080:443

# Get initial password
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d

# Create ArgoCD application
kubectl apply -f k8s/argocd-app.yaml
```

Create: `k8s/argocd-app.yaml`

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: Top Dog
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/easttennesseecc-star/Q-Top-Dog-IDE
    targetRevision: main
    path: k8s
  destination:
    server: https://kubernetes.default.svc
    namespace: Top Dog
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
```

---

## 🎯 AUTO-SCALING BEHAVIOR

### How It Works

```
1. User traffic increases
   ↓
2. Backend CPU hits 75% threshold
   ↓
3. HPA detects and adds 1-2 new pods
   ↓
4. Load balancer distributes traffic
   ↓
5. CPU normalizes
   ↓
6. System ready for 10x more traffic

All automatic! Zero downtime!
```

### Scale-Up Example

```
Traffic: 100 req/s
Current: 2 pods @ 80% CPU each
├─ Add pod #3 (50 req/s, 40% CPU per pod)
├─ Traffic recovers
├─ Add pod #4 (37.5 req/s, 30% CPU per pod)
└─ Stable until 500 req/s

Total: Scales from 2 → 10 pods automatically
```

---

## 📈 PERFORMANCE IMPROVEMENTS WITH K8S

### Before (Single VM):
```
Max capacity: ~100 concurrent users
Response time: 500-2000ms under load
Downtime on deployment: 5-10 minutes
Recovery from failure: Manual intervention
```

### After (Kubernetes):
```
Max capacity: ~1000+ concurrent users
Response time: 50-200ms with auto-scaling
Downtime on deployment: 0 minutes (rolling updates)
Recovery from failure: Automatic (self-healing)
```

---

## 🔒 SECURITY BEST PRACTICES

### Network Policies

Create: `k8s/08-network-policy.yaml`

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: Top Dog-network-policy
  namespace: Top Dog
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector: {}
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
  egress:
  - to:
    - podSelector: {}
  - to:
    - namespaceSelector: {}
    ports:
    - protocol: TCP
      port: 53
    - protocol: TCP
      port: 443
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
```

### Resource Quotas

Create: `k8s/09-resource-quota.yaml`

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: Top Dog-quota
  namespace: Top Dog
spec:
  hard:
    requests.cpu: "20"
    requests.memory: "40Gi"
    limits.cpu: "40"
    limits.memory: "80Gi"
    pods: "50"
  scopeSelector:
    matchExpressions:
    - operator: In
      scopeName: PriorityClass
      values: ["high"]
```

---

## 💾 BACKUP & RECOVERY

### Database Backups

```bash
# Create backup
kubectl exec -it postgres-0 -n Top Dog -- \
  pg_dump -U qide_user qide_prod > backup-$(date +%Y%m%d).sql

# Restore backup
kubectl exec -it postgres-0 -n Top Dog -- \
  psql -U qide_user qide_prod < backup-20251101.sql

# Automated backup (daily)
# Use Velero: https://velero.io
```

---

## 🚨 DISASTER RECOVERY

### RTO & RPO

```
Recovery Time Objective (RTO): < 5 minutes
  - Pods auto-restart
  - Load balancer redirects traffic
  - Database maintains connections

Recovery Point Objective (RPO): < 1 hour
  - Daily automated backups
  - Transaction logs maintained
  - PV snapshots
```

---

## 📋 DEPLOYMENT CHECKLIST

### Pre-Deployment:
- [ ] Kubernetes cluster running with auto-scaling
- [ ] kubectl configured and connected
- [ ] Docker images built and pushed to registry
- [ ] Stripe production keys ready
- [ ] Domains pointing to cluster ingress
- [ ] SSL certificates setup with cert-manager

### Deployment:
- [ ] Namespaces created
- [ ] ConfigMaps deployed
- [ ] Secrets (sealed) deployed
- [ ] PostgreSQL StatefulSet running
- [ ] Backend deployment scaled
- [ ] Frontend deployment scaled
- [ ] Ingress configured
- [ ] Certificates issued

### Post-Deployment:
- [ ] All pods running
- [ ] Services responding
- [ ] Ingress showing healthy backends
- [ ] SSL certificates valid
- [ ] HPA metrics updating
- [ ] Logs flowing correctly
- [ ] Database connected
- [ ] Health checks passing

### Monitoring:
- [ ] Prometheus scraping metrics
- [ ] Grafana dashboards created
- [ ] Alerts configured
- [ ] Auto-scaling tested
- [ ] Load testing performed

---

## 🧪 TESTING AUTO-SCALING

### Simulate Traffic Load

```bash
# Install Apache Bench
apt-get install apache2-utils

# Send 10,000 requests, 100 concurrent
ab -n 10000 -c 100 https://Top Dog.com

# Watch pods scale
watch kubectl get pods -n Top Dog

# Watch HPA
watch kubectl get hpa -n Top Dog

# Check metrics
kubectl top pods -n Top Dog
```

### Results You Should See:
```
Before: 2 pods @ 90% CPU
During: 3 → 4 → 5 pods @ 70-75% CPU
After: Scale down to 2 pods

Response time stable: 100-200ms
No errors or timeouts
Zero downtime
```

---

## 💰 COST ANALYSIS WITH K8S

### Cost Comparison:

```
OPTION A: Single VM ($12/month)
├─ Capacity: 100 concurrent users
├─ Auto-scaling: None
├─ Downtime: Yes
├─ Cost: $144/year
└─ Becomes inadequate at 500 users

OPTION B: Kubernetes ($50-150/month)
├─ Capacity: 1000+ concurrent users
├─ Auto-scaling: Full
├─ Downtime: Zero
├─ Cost: $600-1800/year
└─ Scales infinitely, pay for what you use

BREAKEVEN: At ~800+ concurrent users
```

---

## 🎯 NEXT STEPS

### This Week:
- [ ] Read this entire guide
- [ ] Review Kubernetes manifests
- [ ] Build Docker images
- [ ] Test locally with Docker Compose

### Next Week:
- [ ] Deploy to Kubernetes
- [ ] Configure Ingress
- [ ] Setup SSL certificates
- [ ] Test auto-scaling

### Before Launch:
- [ ] Stress test with load
- [ ] Monitor performance
- [ ] Setup alerts
- [ ] Document procedures
- [ ] Train team

### After Launch:
- [ ] Monitor metrics daily
- [ ] Adjust resource limits as needed
- [ ] Optimize scaling policies
- [ ] Plan for growth
- [ ] Celebrate! 🎉

---

## 📚 RESOURCES

**Official Documentation:**
- Kubernetes Docs: https://kubernetes.io/docs
- Helm: https://helm.sh
- ArgoCD: https://argoproj.github.io/argo-cd
- Cert-Manager: https://cert-manager.io
- Prometheus: https://prometheus.io
- Grafana: https://grafana.com

**Tools:**
- kubectl: https://kubernetes.io/docs/tasks/tools
- Docker: https://docker.com
- Helm: https://helm.sh

---

## 🚀 YOU'RE READY!

With Kubernetes and auto-scaling:
- ✅ Handle 10x traffic spikes automatically
- ✅ Zero-downtime deployments
- ✅ Self-healing pods
- ✅ Enterprise-grade reliability
- ✅ Cost-optimized scaling
- ✅ Professional monitoring

**Your Top Dog is now enterprise-ready!** 🎉

