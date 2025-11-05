# 📊 Prometheus & Grafana Monitoring Setup Guide

**Purpose**: Production-grade monitoring, metrics collection, and visualization  
**Status**: Complete deployment guide  
**Includes**: Metrics collection, dashboards, alerting

---

## ✅ Step 1: Create Monitoring Namespace

```bash
kubectl create namespace monitoring
```

---

## ✅ Step 2: Install Prometheus

### 2.1 Create Prometheus Namespace & ServiceAccount

```bash
kubectl create sa prometheus -n monitoring
```

### 2.2 Create Prometheus ConfigMap

Create file: `k8s/08-prometheus-config.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: monitoring
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
      evaluation_interval: 15s
      external_labels:
        cluster: 'Top Dog-production'
    
    scrape_configs:
    # Kubernetes API Server
    - job_name: 'kubernetes-apiservers'
      kubernetes_sd_configs:
      - role: endpoints
      scheme: https
      tls_config:
        ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
      bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
      relabel_configs:
      - source_labels: [__meta_kubernetes_namespace, __meta_kubernetes_service_name, __meta_kubernetes_endpoint_port_name]
        action: keep
        regex: default;kubernetes;https

    # Top Dog Backend Metrics
    - job_name: 'Top Dog-backend'
      static_configs:
      - targets: ['backend:8000']
      metrics_path: '/metrics'
      scrape_interval: 10s

    # Top Dog Frontend (if exposed)
    - job_name: 'Top Dog-frontend'
      static_configs:
      - targets: ['frontend:3000']
      metrics_path: '/metrics'
      scrape_interval: 30s

    # PostgreSQL (if exporter available)
    - job_name: 'postgres'
      static_configs:
      - targets: ['postgres-exporter:9187']
      scrape_interval: 30s

    # Kubernetes Nodes
    - job_name: 'kubernetes-nodes'
      kubernetes_sd_configs:
      - role: node
      scheme: https
      tls_config:
        ca_file: /var/run/secrets/kubernetes.io/serviceaccount/ca.crt
      bearer_token_file: /var/run/secrets/kubernetes.io/serviceaccount/token
      relabel_configs:
      - action: labelmap
        regex: __meta_kubernetes_node_label_(.+)

    # Pod Metrics
    - job_name: 'kubernetes-pods'
      kubernetes_sd_configs:
      - role: pod
      relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: 'true'
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        action: replace
        regex: ([^:]+)(?::\d+)?;(\d+)
        replacement: $1:$2
        target_label: __address__
```

### 2.3 Create Prometheus Deployment

Create file: `k8s/08-prometheus-deployment.yaml`

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: prometheus-data
  namespace: monitoring
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      serviceAccountName: prometheus
      containers:
      - name: prometheus
        image: prom/prometheus:latest
        ports:
        - containerPort: 9090
        args:
          - '--config.file=/etc/prometheus/prometheus.yml'
          - '--storage.tsdb.path=/prometheus'
          - '--storage.tsdb.retention.time=30d'
        volumeMounts:
        - name: config
          mountPath: /etc/prometheus
        - name: data
          mountPath: /prometheus
        resources:
          requests:
            cpu: 250m
            memory: 512Mi
          limits:
            cpu: 500m
            memory: 1Gi
        livenessProbe:
          httpGet:
            path: /-/healthy
            port: 9090
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /-/ready
            port: 9090
          initialDelaySeconds: 10
          periodSeconds: 5
      volumes:
      - name: config
        configMap:
          name: prometheus-config
      - name: data
        persistentVolumeClaim:
          claimName: prometheus-data

---
apiVersion: v1
kind: Service
metadata:
  name: prometheus
  namespace: monitoring
spec:
  selector:
    app: prometheus
  ports:
  - port: 9090
    targetPort: 9090
    name: web
  type: ClusterIP
```

### 2.4 Create Prometheus ServiceAccount & RBAC

Create file: `k8s/08-prometheus-rbac.yaml`

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: prometheus
rules:
- apiGroups: [""]
  resources:
  - nodes
  - nodes/proxy
  - services
  - endpoints
  - pods
  verbs: ["get", "list", "watch"]
- apiGroups:
  - extensions
  resources:
  - ingresses
  verbs: ["get", "list", "watch"]
- nonResourceURLs: ["/metrics"]
  verbs: ["get"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: prometheus
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: prometheus
subjects:
- kind: ServiceAccount
  name: prometheus
  namespace: monitoring

---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: prometheus
  namespace: monitoring
```

### 2.5 Deploy Prometheus

```bash
kubectl apply -f k8s/08-prometheus-rbac.yaml
kubectl apply -f k8s/08-prometheus-config.yaml
kubectl apply -f k8s/08-prometheus-deployment.yaml

# Verify
kubectl get pods -n monitoring
kubectl get svc -n monitoring
```

---

## ✅ Step 3: Install Grafana

### 3.1 Create Grafana Deployment

Create file: `k8s/09-grafana-deployment.yaml`

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: grafana-data
  namespace: monitoring
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-datasources
  namespace: monitoring
data:
  prometheus.yaml: |
    apiVersion: 1
    datasources:
    - name: Prometheus
      type: prometheus
      access: proxy
      url: http://prometheus:9090
      isDefault: true
      editable: true

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grafana
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: grafana
  template:
    metadata:
      labels:
        app: grafana
    spec:
      containers:
      - name: grafana
        image: grafana/grafana:latest
        ports:
        - containerPort: 3000
        env:
        - name: GF_SECURITY_ADMIN_PASSWORD
          value: "admin"  # CHANGE THIS IN PRODUCTION
        - name: GF_SECURITY_ADMIN_USER
          value: "admin"
        - name: GF_INSTALL_PLUGINS
          value: "grafana-worldmap-panel"
        volumeMounts:
        - name: storage
          mountPath: /var/lib/grafana
        - name: datasources
          mountPath: /etc/grafana/provisioning/datasources
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
        livenessProbe:
          httpGet:
            path: /api/health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/health
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 5
      volumes:
      - name: storage
        persistentVolumeClaim:
          claimName: grafana-data
      - name: datasources
        configMap:
          name: grafana-datasources

---
apiVersion: v1
kind: Service
metadata:
  name: grafana
  namespace: monitoring
spec:
  selector:
    app: grafana
  ports:
  - port: 3000
    targetPort: 3000
    name: web
  type: ClusterIP
```

### 3.2 Deploy Grafana

```bash
kubectl apply -f k8s/09-grafana-deployment.yaml

# Verify
kubectl get pods -n monitoring -l app=grafana
kubectl get svc -n monitoring
```

---

## ✅ Step 4: Expose Monitoring Services

### 4.1 Add Ingress Routes

Create file: `k8s/10-monitoring-ingress.yaml`

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: monitoring-ingress
  namespace: monitoring
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - prometheus.Top Dog.com
    - grafana.Top Dog.com
    secretName: monitoring-tls
  rules:
  - host: prometheus.Top Dog.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: prometheus
            port:
              number: 9090
  - host: grafana.Top Dog.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: grafana
            port:
              number: 3000
```

### 4.2 Deploy Ingress

```bash
kubectl apply -f k8s/10-monitoring-ingress.yaml

# Add DNS records for monitoring subdomain
# prometheus.Top Dog.com  A  134.199.134.151
# grafana.Top Dog.com     A  134.199.134.151
```

---

## ✅ Step 5: Access & Configure

### 5.1 Access Grafana

1. **Via Ingress**: https://grafana.Top Dog.com (after DNS configured)
2. **Via Port-Forward**: 
   ```bash
   kubectl port-forward svc/grafana 3000:3000 -n monitoring
   # Then open: http://localhost:3000
   ```

### 5.2 Login to Grafana

```
Username: admin
Password: admin
```

⚠️ **IMPORTANT**: Change the admin password immediately after login!

### 5.3 Add Prometheus Data Source

1. Login to Grafana
2. Go to Configuration → Data Sources → Add data source
3. Select "Prometheus"
4. Set URL to: `http://prometheus:9090`
5. Click "Save & Test"

### 5.4 Import Dashboards

**Option A: Use Pre-built Dashboards**

1. Go to Dashboards → Browse → Import
2. Search Grafana dashboard library (https://grafana.com/grafana/dashboards/)
3. Recommended dashboards:
   - **Kubernetes Cluster Monitoring** (ID: 7249)
   - **Node Exporter for Prometheus** (ID: 11074)
   - **Prometheus 2.0 Stats** (ID: 3662)

**Option B: Create Custom Dashboard**

1. New Dashboard → Add Panel
2. Select Prometheus as data source
3. Query examples:
   ```promql
   # CPU usage
   rate(container_cpu_usage_seconds_total[5m])
   
   # Memory usage
   container_memory_usage_bytes
   
   # Pod restarts
   increase(kube_pod_container_status_restarts_total[1h])
   
   # API request rate
   rate(http_requests_total[5m])
   ```

---

## ⚙️ Step 6: Alerting Configuration

### 6.1 Create AlertManager Config

Create file: `k8s/11-alertmanager-config.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: alertmanager-config
  namespace: monitoring
data:
  config.yml: |
    global:
      resolve_timeout: 5m
    
    route:
      receiver: 'default'
      group_wait: 30s
      group_interval: 5m
      repeat_interval: 4h
      routes:
      - match:
          severity: critical
        receiver: 'critical'
        repeat_interval: 1h
    
    receivers:
    - name: 'default'
    - name: 'critical'
      # Add webhook, email, slack, etc.
      # webhook_configs:
      # - url: 'http://webhook-receiver:5001/alert'
```

### 6.2 Alert Rules

Create file: `k8s/11-prometheus-rules.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-rules
  namespace: monitoring
data:
  alerts.yml: |
    groups:
    - name: kubernetes.rules
      interval: 30s
      rules:
      # Pod Restart Alert
      - alert: PodRestartingTooOften
        expr: rate(kube_pod_container_status_restarts_total[15m]) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Pod {{ $labels.pod }} in {{ $labels.namespace }} is restarting frequently"
      
      # High CPU Usage
      - alert: HighCPUUsage
        expr: |
          (sum(rate(container_cpu_usage_seconds_total[5m])) by (pod, namespace) 
           / sum(container_spec_cpu_quota/container_spec_cpu_period) by (pod, namespace)) > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected in {{ $labels.pod }}"
      
      # High Memory Usage
      - alert: HighMemoryUsage
        expr: |
          (sum(container_memory_usage_bytes) by (pod, namespace) 
           / sum(container_spec_memory_limit_bytes) by (pod, namespace)) > 0.8
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage detected in {{ $labels.pod }}"
      
      # Pod Not Ready
      - alert: PodNotReady
        expr: kube_pod_status_ready{condition="false"} == 1
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "Pod {{ $labels.pod }} in {{ $labels.namespace }} not ready"
```

---

## 🧪 Verification

### 7.1 Verify Prometheus is Scraping

```bash
# Port-forward to Prometheus
kubectl port-forward svc/prometheus 9090:9090 -n monitoring

# Visit: http://localhost:9090
# Check:
# - Status → Targets (should show all jobs green)
# - Status → Configuration (verify scrape jobs)
# - Graph → Try: up (shows which targets are healthy)
```

### 7.2 Verify Grafana Connection

```bash
# Port-forward to Grafana
kubectl port-forward svc/grafana 3000:3000 -n monitoring

# Visit: http://localhost:3000
# Login with admin/admin
# Check: Configuration → Data Sources (Prometheus should be connected)
```

### 7.3 Check Metrics Collection

```bash
# Query metrics from Prometheus
curl http://prometheus:9090/api/v1/query?query=up

# Should return JSON with targets and their status
```

---

## 📋 Deployment Checklist

- [ ] Monitoring namespace created
- [ ] Prometheus ConfigMap deployed
- [ ] Prometheus Deployment running (1/1 Ready)
- [ ] Prometheus Service accessible
- [ ] Grafana Deployment running (1/1 Ready)
- [ ] Grafana Service accessible
- [ ] Ingress routes created for monitoring services
- [ ] DNS records added (prometheus.Top Dog.com, grafana.Top Dog.com)
- [ ] Grafana accessible via web (http://localhost:3000)
- [ ] Prometheus data source connected in Grafana
- [ ] At least one dashboard imported
- [ ] Alert rules configured
- [ ] AlertManager ready for notifications

---

## ✅ Success Criteria

```
✅ kubectl get pods -n monitoring shows 2 pods (prometheus, grafana) with 1/1 Ready
✅ Prometheus scrapes targets (Status → Targets shows all green)
✅ Grafana dashboard accessible (http://localhost:3000)
✅ Prometheus data source connected in Grafana
✅ Dashboards display metrics (CPU, Memory, Pods, etc.)
✅ Alert rules configured and active
✅ No errors in pod logs
```

---

## 📚 Quick Reference

```bash
# Deploy all monitoring components
kubectl apply -f k8s/08-prometheus-rbac.yaml
kubectl apply -f k8s/08-prometheus-config.yaml
kubectl apply -f k8s/08-prometheus-deployment.yaml
kubectl apply -f k8s/09-grafana-deployment.yaml
kubectl apply -f k8s/10-monitoring-ingress.yaml
kubectl apply -f k8s/11-prometheus-rules.yaml

# Access services locally
kubectl port-forward svc/prometheus 9090:9090 -n monitoring
kubectl port-forward svc/grafana 3000:3000 -n monitoring

# View logs
kubectl logs -n monitoring -l app=prometheus -f
kubectl logs -n monitoring -l app=grafana -f

# Check metrics in Prometheus
curl http://prometheus:9090/api/v1/targets
```

---

**Status**: 🟡 Ready for Installation  
**Complexity**: ⭐⭐⭐ High (30-45 minutes)  
**Impact**: Critical for production observability  
**Maintenance**: Automatic collection, dashboard organization needed
