# 📊 Monitoring Setup with Prometheus & Grafana

**Status**: Complete guide to production monitoring

---

## Overview

This guide sets up Prometheus for metrics collection and Grafana for visualization.

**What You'll Get**:
- ✅ Real-time Kubernetes metrics
- ✅ Application performance monitoring
- ✅ Pod/Node resource usage
- ✅ Network traffic analysis
- ✅ Beautiful dashboards
- ✅ Alert capabilities

---

## Architecture

```
Prometheus (Metrics Collection)
    ↓
Scrapes metrics from:
- Kubernetes API
- Nodes
- Pods
- Services
    ↓
Grafana (Visualization)
    ↓
Beautiful Dashboards
```

---

## Step 1: Add Prometheus Helm Repository

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
```

---

## Step 2: Install Prometheus Stack

This installs Prometheus, Grafana, AlertManager, and more:

```bash
# Create monitoring namespace
kubectl create namespace monitoring

# Install Prometheus stack
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --set grafana.adminPassword=admin \
  --set prometheus.prometheusSpec.retention=30d \
  --set prometheus.prometheusSpec.storageSpec.volumeClaimTemplate.spec.resources.requests.storage=50Gi
```

**Verify Installation**:
```bash
kubectl get pods -n monitoring
# Should see: prometheus-operator, prometheus, grafana, alertmanager, node-exporter pods
```

---

## Step 3: Create Storage for Prometheus

Prometheus needs persistent storage for metrics:

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: prometheus-storage
  namespace: monitoring
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 50Gi
EOF
```

---

## Step 4: Access Grafana Dashboard

### Option A: Port Forward
```bash
# Forward Grafana to localhost
kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring

# Open browser
http://localhost:3000

# Login with:
# Username: admin
# Password: admin (or the one you set)
```

### Option B: Create Ingress for Grafana
```bash
cat <<EOF | kubectl apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: grafana-ingress
  namespace: monitoring
spec:
  ingressClassName: nginx
  rules:
  - host: grafana.Top Dog.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: prometheus-grafana
            port:
              number: 80
EOF
```

Then access at: `http://grafana.Top Dog.com` (after adding DNS record)

---

## Step 5: Add Kubernetes Dashboards

After logging in to Grafana:

1. **Import Default Dashboard**:
   - Click "+" → Import
   - Dashboard ID: `6417` (Kubernetes Cluster Monitoring)
   - Select Prometheus data source
   - Click Import

2. **Add Cluster Dashboard**:
   - Dashboard ID: `7249` (Kubernetes Cluster)
   - Repeat import process

3. **Node Exporter Dashboard**:
   - Dashboard ID: `1860` (Node Exporter for Prometheus)

---

## Step 6: Create Custom Dashboards

### Top Dog Application Metrics

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-dashboard-qide
  namespace: monitoring
data:
  qide-dashboard.json: |
    {
      "dashboard": {
        "title": "Top Dog Application Metrics",
        "panels": [
          {
            "title": "Pod Count",
            "targets": [{"expr": "count(kube_pod_info{namespace=\"Top Dog\"})"}]
          },
          {
            "title": "CPU Usage by Pod",
            "targets": [{"expr": "rate(container_cpu_usage_seconds_total{namespace=\"Top Dog\"}[5m])"}]
          },
          {
            "title": "Memory Usage by Pod",
            "targets": [{"expr": "container_memory_usage_bytes{namespace=\"Top Dog\"}"}]
          },
          {
            "title": "Network I/O",
            "targets": [{"expr": "rate(container_network_transmit_bytes_total{namespace=\"Top Dog\"}[5m])"}]
          }
        ]
      }
    }
EOF
```

---

## Step 7: Configure Prometheus for Your App

Create ServiceMonitor to scrape your backend metrics:

```bash
cat <<EOF | kubectl apply -f -
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: backend-monitor
  namespace: Top Dog
spec:
  selector:
    matchLabels:
      app: backend
  endpoints:
  - port: metrics
    interval: 30s
    path: /metrics
---
apiVersion: v1
kind: Service
metadata:
  name: backend-metrics
  namespace: Top Dog
  labels:
    app: backend
spec:
  ports:
  - name: metrics
    port: 8001
    targetPort: 8001
  selector:
    app: backend
EOF
```

Your backend needs to expose metrics on `/metrics` endpoint (FastAPI + Prometheus middleware).

---

## Step 8: Add Prometheus Exporters

### Node Exporter (Already included in stack)
Collects node-level metrics (CPU, memory, disk, network)

### MySQL/PostgreSQL Exporter
```bash
helm install mysql-exporter prometheus-community/prometheus-mysql-exporter \
  --namespace monitoring \
  --set mysql.host=postgres.Top Dog.svc.cluster.local \
  --set mysql.port=5432 \
  --set mysql.user=postgres \
  --set mysql.password=$(kubectl get secret -n Top Dog postgres-secret -o jsonpath='{.data.password}' | base64 -d)
```

---

## Step 9: Set Up Alerts

Create AlertRule for high resource usage:

```bash
cat <<EOF | kubectl apply -f -
apiVersion: monitoring.coreos.com/v1
kind: PrometheusRule
metadata:
  name: Top Dog-alerts
  namespace: monitoring
spec:
  groups:
  - name: Top Dog
    interval: 30s
    rules:
    - alert: PodCrashing
      expr: rate(kube_pod_container_status_restarts_total{namespace="Top Dog"}[5m]) > 0
      annotations:
        summary: "Pod restarting in Top Dog"
    
    - alert: HighMemoryUsage
      expr: container_memory_usage_bytes{namespace="Top Dog"} / container_spec_memory_limit_bytes > 0.8
      annotations:
        summary: "High memory usage detected"
    
    - alert: HighCPUUsage
      expr: rate(container_cpu_usage_seconds_total{namespace="Top Dog"}[5m]) > 0.8
      annotations:
        summary: "High CPU usage detected"
    
    - alert: PodNotReady
      expr: kube_pod_status_ready{namespace="Top Dog", condition="false"} > 0
      annotations:
        summary: "Pod not ready in Top Dog"
EOF
```

---

## Step 10: Configure AlertManager

AlertManager sends alerts to:
- Email
- Slack
- PagerDuty
- Webhook

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: alertmanager-config
  namespace: monitoring
data:
  alertmanager.yml: |
    global:
      resolve_timeout: 5m
    
    route:
      receiver: default-receiver
      group_by: ['alertname', 'cluster', 'service']
    
    receivers:
    - name: default-receiver
      # Slack integration example:
      slack_configs:
      - api_url: YOUR_SLACK_WEBHOOK_URL
        channel: '#alerts'
        title: 'Top Dog Alert'
      
      # Email example:
      email_configs:
      - to: admin@Top Dog.com
        from: alerts@Top Dog.com
        smarthost: smtp.gmail.com:587
        auth_username: your-email@gmail.com
        auth_password: your-app-password
EOF
```

---

## Important Metrics to Monitor

| Metric | Alert Threshold | Action |
|--------|-----------------|--------|
| Pod Restarts | > 0 in 5min | Investigate pod logs |
| Memory Usage | > 80% | Scale pod resources |
| CPU Usage | > 80% | Enable HPA scaling |
| Disk Usage | > 85% | Increase PVC size |
| Pod Not Ready | > 0 | Check ingress/service |
| API Response Time | > 1s | Optimize queries |
| Error Rate | > 1% | Check logs |

---

## Useful Prometheus Queries

```promql
# CPU usage by pod
rate(container_cpu_usage_seconds_total{namespace="Top Dog"}[5m])

# Memory usage by pod
container_memory_usage_bytes{namespace="Top Dog"}

# Pod count
count(kube_pod_info{namespace="Top Dog"})

# Pod restarts
kube_pod_container_status_restarts_total{namespace="Top Dog"}

# Network bytes sent
rate(container_network_transmit_bytes_total{namespace="Top Dog"}[5m])

# Network bytes received
rate(container_network_receive_bytes_total{namespace="Top Dog"}[5m])

# Pod ready status
kube_pod_status_ready{namespace="Top Dog"}
```

---

## Dashboard URLs

```
Prometheus:    http://localhost:9090        (after port-forward)
Grafana:       http://localhost:3000        (after port-forward)
AlertManager:  http://localhost:9093        (after port-forward)
```

---

## Maintenance

### Backup Prometheus Data
```bash
kubectl exec -n monitoring prometheus-0 -- tar czf /tmp/prometheus-backup.tar.gz /prometheus
kubectl cp monitoring/prometheus-0:/tmp/prometheus-backup.tar.gz ./prometheus-backup.tar.gz
```

### Update Prometheus
```bash
helm upgrade prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --values values.yaml
```

### View Prometheus Targets
```bash
# Port-forward to Prometheus
kubectl port-forward svc/prometheus-operated 9090:9090 -n monitoring

# Visit http://localhost:9090/targets
```

---

## Next Steps

- ✅ Monitoring set up
- ⏳ Configure backups: See POSTGRES_BACKUP_SETUP.md
- ⏳ SSL certificates: See TLS_CERTIFICATE_SETUP.md

---

**Your Top Dog deployment is now fully monitored!**
