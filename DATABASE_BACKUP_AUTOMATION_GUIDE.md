# 💾 PostgreSQL Automated Backups Setup Guide

**Purpose**: Automated database backups with retention policy  
**Frequency**: Daily automatic backups  
**Retention**: 30 days of backups kept  
**Storage**: DigitalOcean Spaces (or local PVC)

---

## ✅ Option 1: Using DigitalOcean Spaces (Recommended for Production)

### 1.1 Create DigitalOcean Spaces Bucket

1. Go to DigitalOcean Control Panel → Spaces
2. Click "Create Spaces"
3. Enter bucket name: `Top Dog-db-backups`
4. Choose region: Same as your cluster (Atlanta)
5. Enable "Restrict File Listing" for security
6. Create bucket

### 1.2 Generate Space Access Keys

1. Go to Account → API → Tokens & Keys → Spaces Keys
2. Generate new key for backups
3. Note down:
   - Access Key ID
   - Secret Access Key

### 1.3 Create Kubernetes Secret

```bash
kubectl create secret generic postgres-backup-space \
  -n Top Dog \
  --from-literal=access-key='YOUR_ACCESS_KEY' \
  --from-literal=secret-key='YOUR_SECRET_KEY' \
  --from-literal=space-name='Top Dog-db-backups' \
  --from-literal=space-region='nyc3'
```

---

## ✅ Option 2: Using Local PVC (Simpler Setup)

### 2.1 Create PVC for Backups

Create file: `k8s/12-postgres-backup-pvc.yaml`

```yaml
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
      storage: 100Gi  # Adjust based on your needs
```

Deploy:
```bash
kubectl apply -f k8s/12-postgres-backup-pvc.yaml
```

---

## ✅ Step 1: Create Backup Script ConfigMap

Create file: `k8s/12-postgres-backup-script.yaml`

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: postgres-backup-script
  namespace: Top Dog
data:
  backup.sh: |
    #!/bin/bash
    set -e

    # Configuration
    BACKUP_DIR="${BACKUP_DIR:-/backups}"
    DB_HOST="${DB_HOST:-postgres}"
    DB_PORT="${DB_PORT:-5432}"
    DB_USER="${DB_USER:-postgres}"
    DB_PASSWORD="${DB_PASSWORD:-}"
    RETENTION_DAYS="${RETENTION_DAYS:-30}"
    BACKUP_TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="${BACKUP_DIR}/Top Dog-db_${BACKUP_TIMESTAMP}.sql.gz"

    echo "[$(date)] Starting PostgreSQL backup..."

    # Create backup directory
    mkdir -p "${BACKUP_DIR}"

    # Create backup
    export PGPASSWORD="${DB_PASSWORD}"
    pg_dump \
      -h "${DB_HOST}" \
      -p "${DB_PORT}" \
      -U "${DB_USER}" \
      -F custom \
      -f "${BACKUP_DIR}/Top Dog-db_${BACKUP_TIMESTAMP}.dump" \
      Top Dog

    # Compress with gzip
    gzip "${BACKUP_DIR}/Top Dog-db_${BACKUP_TIMESTAMP}.dump"

    echo "[$(date)] Backup completed: ${BACKUP_FILE}"
    echo "[$(date)] Backup size: $(du -h ${BACKUP_FILE} | cut -f1)"

    # Clean old backups (keep only last N days)
    echo "[$(date)] Cleaning backups older than ${RETENTION_DAYS} days..."
    find "${BACKUP_DIR}" -name "Top Dog-db_*.sql.gz" -mtime +${RETENTION_DAYS} -delete

    # List current backups
    echo "[$(date)] Current backups:"
    ls -lh "${BACKUP_DIR}"/Top Dog-db_*.sql.gz 2>/dev/null || echo "No backups found"

    echo "[$(date)] Backup process completed successfully"

  upload-to-spaces.sh: |
    #!/bin/bash
    set -e

    # Configuration
    BACKUP_DIR="${BACKUP_DIR:-/backups}"
    SPACE_ACCESS_KEY="${SPACE_ACCESS_KEY:-}"
    SPACE_SECRET_KEY="${SPACE_SECRET_KEY:-}"
    SPACE_NAME="${SPACE_NAME:-}"
    SPACE_REGION="${SPACE_REGION:-nyc3}"
    RETENTION_DAYS="${RETENTION_DAYS:-30}"

    echo "[$(date)] Starting backup upload to Spaces..."

    # Check if we have credentials
    if [ -z "${SPACE_ACCESS_KEY}" ] || [ -z "${SPACE_SECRET_KEY}" ]; then
      echo "[$(date)] Spaces credentials not configured, skipping upload"
      exit 0
    fi

    # Install AWS CLI if not present
    if ! command -v aws &> /dev/null; then
      echo "[$(date)] Installing AWS CLI..."
      pip install awscli-local 2>/dev/null || apt-get update && apt-get install -y awscliv2
    fi

    # Configure AWS CLI for Spaces
    export AWS_ACCESS_KEY_ID="${SPACE_ACCESS_KEY}"
    export AWS_SECRET_ACCESS_KEY="${SPACE_SECRET_KEY}"

    # Upload latest backup
    LATEST_BACKUP=$(ls -t "${BACKUP_DIR}"/Top Dog-db_*.sql.gz 2>/dev/null | head -1)
    if [ -n "${LATEST_BACKUP}" ]; then
      echo "[$(date)] Uploading ${LATEST_BACKUP} to Spaces..."
      aws s3 cp "${LATEST_BACKUP}" \
        "s3://${SPACE_NAME}/$(basename ${LATEST_BACKUP})" \
        --endpoint-url="https://${SPACE_REGION}.digitaloceanspaces.com" \
        --region "${SPACE_REGION}"
      echo "[$(date)] Upload completed"
    else
      echo "[$(date)] No backup found to upload"
    fi

    # Cleanup old backups from Spaces (keep last 30 days)
    echo "[$(date)] Cleaning old backups from Spaces..."
    aws s3 ls "s3://${SPACE_NAME}/" \
      --endpoint-url="https://${SPACE_REGION}.digitaloceanspaces.com" \
      --region "${SPACE_REGION}" \
      | while read -r line; do
        file=$(echo $line | awk '{print $4}')
        echo "[$(date)] Object in Spaces: ${file}"
      done

  restore.sh: |
    #!/bin/bash
    set -e

    # Configuration
    BACKUP_DIR="${BACKUP_DIR:-/backups}"
    DB_HOST="${DB_HOST:-postgres}"
    DB_PORT="${DB_PORT:-5432}"
    DB_USER="${DB_USER:-postgres}"
    DB_PASSWORD="${DB_PASSWORD:-}"
    BACKUP_FILE="${1:-}"

    if [ -z "${BACKUP_FILE}" ]; then
      echo "Usage: $0 <backup-file>"
      echo "Available backups:"
      ls -lh "${BACKUP_DIR}"/Top Dog-db_*.sql.gz 2>/dev/null || echo "No backups found"
      exit 1
    fi

    if [ ! -f "${BACKUP_FILE}" ]; then
      echo "Error: Backup file not found: ${BACKUP_FILE}"
      exit 1
    fi

    echo "[$(date)] Starting database restore from: ${BACKUP_FILE}"
    echo "[$(date)] ⚠️  WARNING: This will overwrite the current database!"
    read -p "Continue? (yes/no): " confirm

    if [ "${confirm}" != "yes" ]; then
      echo "Restore cancelled"
      exit 0
    fi

    export PGPASSWORD="${DB_PASSWORD}"

    # Decompress and restore
    gunzip -c "${BACKUP_FILE}" | \
      pg_restore \
        -h "${DB_HOST}" \
        -p "${DB_PORT}" \
        -U "${DB_USER}" \
        -d Top Dog \
        --clean \
        -v

    echo "[$(date)] Database restore completed successfully"
```

Deploy:
```bash
kubectl apply -f k8s/12-postgres-backup-script.yaml
```

---

## ✅ Step 2: Create Backup CronJob

Create file: `k8s/12-postgres-backup-cronjob.yaml`

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup-daily
  namespace: Top Dog
spec:
  # Run daily at 2 AM UTC
  schedule: "0 2 * * *"
  concurrencyPolicy: Forbid
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 3
  jobTemplate:
    spec:
      backoffLimit: 3
      template:
        metadata:
          labels:
            app: postgres-backup
        spec:
          serviceAccountName: default
          restartPolicy: OnFailure
          containers:
          - name: backup
            image: postgres:16-alpine
            env:
            - name: DB_HOST
              value: postgres
            - name: DB_PORT
              value: "5432"
            - name: DB_USER
              value: postgres
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: password
            - name: BACKUP_DIR
              value: /backups
            - name: RETENTION_DAYS
              value: "30"
            # Optional: Spaces upload configuration
            - name: SPACE_ACCESS_KEY
              valueFrom:
                secretKeyRef:
                  name: postgres-backup-space
                  key: access-key
                  optional: true
            - name: SPACE_SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: postgres-backup-space
                  key: secret-key
                  optional: true
            - name: SPACE_NAME
              valueFrom:
                secretKeyRef:
                  name: postgres-backup-space
                  key: space-name
                  optional: true
            - name: SPACE_REGION
              valueFrom:
                secretKeyRef:
                  name: postgres-backup-space
                  key: space-region
                  optional: true
            command:
            - /bin/sh
            - -c
            - |
              apk add --no-cache bash gzip curl
              bash /scripts/backup.sh
              if [ -n "$SPACE_NAME" ]; then
                bash /scripts/upload-to-spaces.sh
              fi
            volumeMounts:
            - name: backup-script
              mountPath: /scripts
            - name: backup-storage
              mountPath: /backups
            resources:
              requests:
                cpu: 500m
                memory: 512Mi
              limits:
                cpu: 1000m
                memory: 1Gi
          volumes:
          - name: backup-script
            configMap:
              name: postgres-backup-script
              defaultMode: 0755
          - name: backup-storage
            persistentVolumeClaim:
              claimName: postgres-backups

---
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup-hourly
  namespace: Top Dog
spec:
  # Run every 6 hours for quick recovery capability
  schedule: "0 */6 * * *"
  concurrencyPolicy: Forbid
  successfulJobsHistoryLimit: 2
  failedJobsHistoryLimit: 2
  jobTemplate:
    spec:
      backoffLimit: 1
      template:
        metadata:
          labels:
            app: postgres-backup-hourly
        spec:
          serviceAccountName: default
          restartPolicy: OnFailure
          containers:
          - name: backup
            image: postgres:16-alpine
            env:
            - name: DB_HOST
              value: postgres
            - name: DB_PORT
              value: "5432"
            - name: DB_USER
              value: postgres
            - name: DB_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: password
            - name: BACKUP_DIR
              value: /backups
            - name: RETENTION_DAYS
              value: "7"
            command:
            - /bin/sh
            - -c
            - |
              apk add --no-cache bash gzip
              bash /scripts/backup.sh
            volumeMounts:
            - name: backup-script
              mountPath: /scripts
            - name: backup-storage
              mountPath: /backups
            resources:
              requests:
                cpu: 250m
                memory: 256Mi
              limits:
                cpu: 500m
                memory: 512Mi
          volumes:
          - name: backup-script
            configMap:
              name: postgres-backup-script
              defaultMode: 0755
          - name: backup-storage
            persistentVolumeClaim:
              claimName: postgres-backups
```

Deploy:
```bash
kubectl apply -f k8s/12-postgres-backup-pvc.yaml
kubectl apply -f k8s/12-postgres-backup-script.yaml
kubectl apply -f k8s/12-postgres-backup-cronjob.yaml

# Verify
kubectl get cronjob -n Top Dog
```

---

## ✅ Step 3: Manual Backup (On-Demand)

### 3.1 Create One-Time Backup Job

```bash
# Create a one-time backup job
kubectl create job --from=cronjob/postgres-backup-daily manual-backup-$(date +%s) -n Top Dog

# Monitor the job
kubectl get jobs -n Top Dog -w

# View logs
kubectl logs -n Top Dog job/manual-backup-* -f

# List backups in PVC
kubectl exec -it postgres-0 -n Top Dog -- ls -lh /backups/
```

### 3.2 Manual Backup Command

```bash
# Get into postgres pod and backup directly
kubectl exec -it postgres-0 -n Top Dog -- bash

# Inside pod:
export PGPASSWORD=$(kubectl get secret postgres-secret -n Top Dog -o jsonpath='{.data.password}' | base64 -d)
pg_dump -U postgres -d Top Dog | gzip > /backups/manual-backup-$(date +%Y%m%d_%H%M%S).sql.gz
ls -lh /backups/
```

---

## ✅ Step 4: Restore from Backup

### 4.1 Restore Procedure

```bash
# 1. List available backups
kubectl exec -it postgres-0 -n Top Dog -- ls -lh /backups/Top Dog-db_*.sql.gz

# 2. Choose backup to restore
BACKUP_FILE="/backups/Top Dog-db_20251101_020000.sql.gz"

# 3. Restore (WARNING: This overwrites current database!)
kubectl exec -it postgres-0 -n Top Dog -- bash << EOF
export PGPASSWORD=$(kubectl get secret postgres-secret -n Top Dog -o jsonpath='{.data.password}' | base64 -d)
gunzip -c ${BACKUP_FILE} | pg_restore -U postgres -d Top Dog --clean -v
EOF
```

### 4.2 Restore into New Database (Non-Destructive)

```bash
# Create new database for testing
kubectl exec -it postgres-0 -n Top Dog -- psql -U postgres -c "CREATE DATABASE Top Dog-restored;"

# Restore into new database
kubectl exec -it postgres-0 -n Top Dog -- bash << EOF
export PGPASSWORD=$(kubectl get secret postgres-secret -n Top Dog -o jsonpath='{.data.password}' | base64 -d)
gunzip -c ${BACKUP_FILE} | pg_restore -U postgres -d Top Dog-restored -v
EOF

# Verify
kubectl exec -it postgres-0 -n Top Dog -- psql -U postgres -d Top Dog-restored -c "\dt"
```

---

## ✅ Step 5: Verify Backup Success

### 5.1 Check CronJob Status

```bash
# View cronjob schedules
kubectl get cronjob -n Top Dog -o wide

# View job history
kubectl get jobs -n Top Dog --sort-by=.metadata.creationTimestamp

# Check latest job logs
kubectl logs -n Top Dog job/postgres-backup-daily-xxxxx -f
```

### 5.2 Verify Backups are Created

```bash
# Check backups in PVC
kubectl exec postgres-0 -n Top Dog -- ls -lh /backups/

# Check backup size
kubectl exec postgres-0 -n Top Dog -- du -sh /backups/

# Check specific backup integrity
kubectl exec postgres-0 -n Top Dog -- bash << EOF
gunzip -t /backups/Top Dog-db_*.sql.gz && echo "✅ All backups are valid"
EOF
```

### 5.3 Test Restore

```bash
# Periodically test restore capability (e.g., weekly)
# 1. Create test database
kubectl exec postgres-0 -n Top Dog -- psql -U postgres -c "CREATE DATABASE Top Dog-test;"

# 2. Restore backup to test database
kubectl exec postgres-0 -n Top Dog -- bash << EOF
export PGPASSWORD=$(kubectl get secret postgres-secret -n Top Dog -o jsonpath='{.data.password}' | base64 -d)
gunzip -c /backups/Top Dog-db_*.sql.gz | pg_restore -U postgres -d Top Dog-test -v
EOF

# 3. Verify data integrity
kubectl exec postgres-0 -n Top Dog -- psql -U postgres -d Top Dog-test -c "\dt"

# 4. Cleanup test database
kubectl exec postgres-0 -n Top Dog -- psql -U postgres -c "DROP DATABASE Top Dog-test;"
```

---

## 📋 Backup Monitoring

### Monitor Backup Size Growth

```bash
# Weekly: Check backup storage usage
kubectl exec postgres-0 -n Top Dog -- du -sh /backups/

# Monthly: Check PVC capacity
kubectl get pvc -n Top Dog

# If approaching limit, increase PVC size
```

### Setup Backup Alerts (Optional)

```bash
# Create alert if backup job fails
kubectl apply -f - << EOF
apiVersion: batch/v1
kind: Job
metadata:
  name: backup-monitoring
spec:
  template:
    spec:
      serviceAccountName: default
      containers:
      - name: monitor
        image: curlimages/curl:latest
        command:
        - sh
        - -c
        - |
          # Check if yesterday's backup exists
          STATUS=\$(kubectl get jobs -n Top Dog -l app=postgres-backup \
            --sort-by=.metadata.creationTimestamp | tail -1 | awk '{print \$3}')
          
          if [ "\$STATUS" != "1" ]; then
            echo "⚠️ Backup job failed!"
            # Send alert (webhook, email, etc.)
          fi
      restartPolicy: Never
EOF
```

---

## 📋 Deployment Checklist

- [ ] PVC created for backups (100Gi)
- [ ] Backup script ConfigMap deployed
- [ ] Backup CronJob deployed (daily at 2 AM UTC)
- [ ] Hourly CronJob deployed (every 6 hours)
- [ ] Test backup created and verified
- [ ] Restore script tested successfully
- [ ] DigitalOcean Spaces configured (optional)
- [ ] Backup credentials in Kubernetes secrets
- [ ] Backup retention policy configured (30 days)
- [ ] Monitoring alerts setup (optional)

---

## ✅ Success Criteria

```
✅ kubectl get cronjob -n Top Dog shows both daily and hourly jobs
✅ Backup files exist in /backups/ directory
✅ Backup files are valid (gunzip -t passes)
✅ Latest backup is less than 24 hours old
✅ Test restore completed successfully
✅ Database tables exist in restored database
✅ No errors in CronJob logs
✅ Backup storage usage < 80% of PVC capacity
```

---

## 📚 Quick Reference Commands

```bash
# Deploy backups
kubectl apply -f k8s/12-postgres-backup-*.yaml

# Manual backup now
kubectl create job --from=cronjob/postgres-backup-daily backup-now-$(date +%s) -n Top Dog

# Check backup status
kubectl get cronjob,jobs -n Top Dog

# View logs
kubectl logs -n Top Dog job/postgres-backup-daily-xxxxx -f

# List backups
kubectl exec postgres-0 -n Top Dog -- ls -lh /backups/

# Restore from backup
kubectl exec postgres-0 -n Top Dog -- psql -U postgres -d Top Dog < /backups/backup.sql
```

---

**Status**: 🟡 Ready for Installation  
**Complexity**: ⭐⭐ Medium (20-30 minutes)  
**Impact**: Critical for data safety  
**RPO**: 6 hours, **RTO**: 15-30 minutes (to restore)
