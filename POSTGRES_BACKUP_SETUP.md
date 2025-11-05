# 💾 PostgreSQL Automated Backup Setup

**Status**: Complete guide to automated database backups

---

## Overview

This guide sets up automated PostgreSQL backups to:
- ✅ Daily backups to persistent storage
- ✅ Weekly backups to DigitalOcean Spaces (S3-compatible)
- ✅ Automatic retention policy
- ✅ Easy restore capability

---

## Architecture

```
PostgreSQL Database (Top Dog)
    ↓
pg_dump (Daily - 5 AM UTC)
    ↓
Persistent Volume (Local)
    ↓
Digital Ocean Spaces (Weekly backup)
    ↓
30-day retention policy
```

---

## Step 1: Create Backup Volume

Create persistent storage for backups:

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-backups
  namespace: Top Dog
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 100Gi
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: postgres-backups-pv
spec:
  capacity:
    storage: 100Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: do-block-storage
EOF
```

---

## Step 2: Create Backup Service Account

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ServiceAccount
metadata:
  name: postgres-backup
  namespace: Top Dog
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: postgres-backup
  namespace: Top Dog
rules:
- apiGroups: [""]
  resources: ["secrets"]
  verbs: ["get", "list"]
- apiGroups: [""]
  resources: ["persistentvolumeclaims"]
  verbs: ["get", "list"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: postgres-backup
  namespace: Top Dog
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: postgres-backup
subjects:
- kind: ServiceAccount
  name: postgres-backup
  namespace: Top Dog
EOF
```

---

## Step 3: Create Backup Secret

Store PostgreSQL connection details:

```bash
kubectl create secret generic postgres-backup-secret \
  --from-literal=PGUSER=postgres \
  --from-literal=PGPASSWORD=$(kubectl get secret -n Top Dog postgres-password -o jsonpath='{.data.password}' | base64 -d) \
  --from-literal=PGHOST=postgres.Top Dog.svc.cluster.local \
  --from-literal=PGPORT=5432 \
  --from-literal=PGDATABASE=qide \
  -n Top Dog
```

---

## Step 4: Create Daily Backup CronJob

This runs every day at 5 AM UTC:

```bash
cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup-daily
  namespace: Top Dog
spec:
  schedule: "0 5 * * *"  # Every day at 5 AM UTC
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: postgres-backup
          containers:
          - name: backup
            image: postgres:16-alpine
            env:
            - name: PGUSER
              valueFrom:
                secretKeyRef:
                  name: postgres-backup-secret
                  key: PGUSER
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgres-backup-secret
                  key: PGPASSWORD
            - name: PGHOST
              valueFrom:
                secretKeyRef:
                  name: postgres-backup-secret
                  key: PGHOST
            - name: PGPORT
              valueFrom:
                secretKeyRef:
                  name: postgres-backup-secret
                  key: PGPORT
            - name: PGDATABASE
              valueFrom:
                secretKeyRef:
                  name: postgres-backup-secret
                  key: PGDATABASE
            volumeMounts:
            - name: backup-storage
              mountPath: /backups
            command:
            - /bin/sh
            - -c
            - |
              set -e
              BACKUP_FILE="/backups/qide-$(date +%Y%m%d-%H%M%S).sql.gz"
              echo "Starting backup to \$BACKUP_FILE..."
              pg_dump -h \$PGHOST -U \$PGUSER -d \$PGDATABASE | gzip > \$BACKUP_FILE
              echo "Backup completed: \$(ls -lh \$BACKUP_FILE)"
              
              # Keep only last 30 days of backups
              find /backups -name "qide-*.sql.gz" -mtime +30 -delete
              echo "Cleanup completed"
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: postgres-backups
          restartPolicy: OnFailure
          backoffLimit: 3
EOF
```

---

## Step 5: Verify Backup Job

```bash
# Check CronJob is created
kubectl get cronjob -n Top Dog

# View CronJob details
kubectl describe cronjob postgres-backup-daily -n Top Dog

# Check backup files
kubectl exec -it postgres-0 -n Top Dog -- ls -lah /backups/

# Manually trigger backup (for testing)
kubectl create job --from=cronjob/postgres-backup-daily manual-backup-test -n Top Dog
```

---

## Step 6: Create Weekly S3 Backup (Optional but Recommended)

Upload backups to DigitalOcean Spaces for off-site storage:

### 6a: Create DigitalOcean Spaces Bucket

```bash
# Via DigitalOcean CLI
doctl compute spaces create Top Dog-backups --region nyc3

# Or via dashboard:
# Manage > Spaces > Create Space > Top Dog-backups
```

### 6b: Create Access Keys

```bash
# Get from: Account > API > Spaces Keys
# Store SPACES_KEY and SPACES_SECRET safely
```

### 6c: Create S3 Upload CronJob

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
metadata:
  name: spaces-credentials
  namespace: Top Dog
type: Opaque
stringData:
  SPACES_KEY: your-spaces-key-here
  SPACES_SECRET: your-spaces-secret-here
  SPACES_BUCKET: Top Dog-backups
  SPACES_REGION: nyc3
  SPACES_ENDPOINT: nyc3.digitaloceanspaces.com
---
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup-s3
  namespace: Top Dog
spec:
  schedule: "0 6 * * 0"  # Every Sunday at 6 AM UTC
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: postgres-backup
          containers:
          - name: s3-upload
            image: amazon/aws-cli:latest
            env:
            - name: AWS_ACCESS_KEY_ID
              valueFrom:
                secretKeyRef:
                  name: spaces-credentials
                  key: SPACES_KEY
            - name: AWS_SECRET_ACCESS_KEY
              valueFrom:
                secretKeyRef:
                  name: spaces-credentials
                  key: SPACES_SECRET
            - name: SPACES_BUCKET
              valueFrom:
                secretKeyRef:
                  name: spaces-credentials
                  key: SPACES_BUCKET
            - name: SPACES_ENDPOINT
              valueFrom:
                secretKeyRef:
                  name: spaces-credentials
                  key: SPACES_ENDPOINT
            volumeMounts:
            - name: backup-storage
              mountPath: /backups
            command:
            - /bin/sh
            - -c
            - |
              set -e
              LATEST_BACKUP=\$(ls -t /backups/qide-*.sql.gz | head -1)
              if [ -z "\$LATEST_BACKUP" ]; then
                echo "No backups found"
                exit 1
              fi
              
              echo "Uploading \$LATEST_BACKUP to S3..."
              aws s3 cp \$LATEST_BACKUP \
                s3://\$SPACES_BUCKET/backups/ \
                --endpoint-url https://\$SPACES_ENDPOINT \
                --region nyc3
              
              echo "Upload completed"
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: postgres-backups
          restartPolicy: OnFailure
EOF
```

---

## Step 7: Test Restore Procedure

### Extract Latest Backup

```bash
# Find latest backup
kubectl exec -it postgres-0 -n Top Dog -- ls -lht /backups/ | head -5

# Copy backup to local machine
kubectl cp Top Dog/postgres-0:/backups/qide-20251101-050000.sql.gz ./backup.sql.gz
```

### Restore to New Database

```bash
# Decompress
gunzip backup.sql.gz

# Restore (when needed)
psql -h postgres.Top Dog.svc.cluster.local -U postgres -d postgres < backup.sql

# Or restore to new database
psql -h postgres.Top Dog.svc.cluster.local -U postgres -c "CREATE DATABASE qide_restored;"
psql -h postgres.Top Dog.svc.cluster.local -U postgres -d qide_restored < backup.sql
```

---

## Step 8: Create Backup Monitoring

Monitor backup completion:

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ConfigMap
metadata:
  name: backup-monitor-script
  namespace: Top Dog
data:
  check-backups.sh: |
    #!/bin/bash
    BACKUP_DIR="/backups"
    TODAY=\$(date +%Y%m%d)
    LATEST=\$(ls -t \$BACKUP_DIR/qide-*.sql.gz 2>/dev/null | head -1)
    
    if [ -z "\$LATEST" ]; then
      echo "❌ No backups found"
      exit 1
    fi
    
    if [[ \$LATEST == *"\$TODAY"* ]]; then
      SIZE=\$(du -h \$LATEST | cut -f1)
      echo "✅ Backup completed today - Size: \$SIZE"
      echo "File: \$LATEST"
      exit 0
    else
      echo "⚠️  No backup from today"
      echo "Latest: \$LATEST"
      exit 1
    fi
EOF

# Create a simple monitoring pod to run this
kubectl create job --image=busybox backup-monitor -n Top Dog \
  -- sh -c 'cat /config/check-backups.sh | sh'
```

---

## Step 9: Backup Retention Policy

Automatic cleanup of old backups:

```bash
# Keep backups for:
# - Local storage: 30 days
# - S3 storage: 90 days

cat <<EOF | kubectl apply -f -
apiVersion: batch/v1
kind: CronJob
metadata:
  name: backup-cleanup
  namespace: Top Dog
spec:
  schedule: "30 6 * * *"  # Daily at 6:30 AM UTC
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: cleanup
            image: alpine:latest
            volumeMounts:
            - name: backup-storage
              mountPath: /backups
            command:
            - /bin/sh
            - -c
            - |
              echo "Cleaning up backups older than 30 days..."
              find /backups -name "qide-*.sql.gz" -mtime +30 -delete -print
              echo "Cleanup completed"
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: postgres-backups
          restartPolicy: OnFailure
EOF
```

---

## Important Commands

```bash
# View backup schedule
kubectl get cronjob -n Top Dog

# Check last backup
kubectl exec -it postgres-0 -n Top Dog -- ls -lh /backups/ | tail -5

# Manual backup (testing)
kubectl create job --from=cronjob/postgres-backup-daily test-backup -n Top Dog

# View backup job logs
kubectl logs -l job-name=test-backup -n Top Dog

# Check backup size
kubectl exec -it postgres-0 -n Top Dog -- du -sh /backups/

# List all backups
kubectl exec -it postgres-0 -n Top Dog -- find /backups -name "*.sql.gz" -exec ls -lh {} \;
```

---

## Backup Strategy

| Backup Type | Frequency | Location | Retention |
|-------------|-----------|----------|-----------|
| Full backup | Daily (5 AM) | Local PVC | 30 days |
| S3 backup | Weekly (Sunday) | DigitalOcean Spaces | 90 days |
| Manual backup | On-demand | As needed | Indefinite |

---

## Disaster Recovery Plan

**If database crashes**:

1. Check if pods are recovering
   ```bash
   kubectl get pods -n Top Dog -l app=postgres
   ```

2. If pod doesn't recover, restore from backup:
   ```bash
   # Delete failed postgres pod
   kubectl delete pod postgres-0 -n Top Dog
   
   # PVC remains, data should be intact
   # Kubernetes will create new pod with existing volume
   ```

3. If data is corrupted, restore from backup:
   ```bash
   # Get latest backup
   BACKUP=$(kubectl exec -it postgres-0 -n Top Dog -- ls -t /backups/qide-*.sql.gz | head -1)
   
   # Create new database
   kubectl exec -it postgres-0 -n Top Dog -- psql -U postgres -c "CREATE DATABASE qide_restored"
   
   # Restore data
   kubectl exec -i postgres-0 -n Top Dog -- psql -U postgres -d qide_restored < /backups/backup.sql
   ```

---

## Verification Checklist

- [ ] Backup PVC created (100GB)
- [ ] Daily CronJob scheduled (5 AM UTC)
- [ ] First backup completed
- [ ] S3 bucket created (for weekly backups)
- [ ] Cleanup policy configured (30-day retention)
- [ ] Restore procedure tested
- [ ] Monitoring alerts configured

---

**Your database is now protected with automated backups!**
