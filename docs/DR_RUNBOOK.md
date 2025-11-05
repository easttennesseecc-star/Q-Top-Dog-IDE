# Disaster Recovery (DR) Runbook

This runbook describes how to prepare for and recover from failures impacting TopDog IDE.

Goals:
- RTO target: 60–120 minutes (recover services)
- RPO target: 1 hour (data loss tolerance)

## 1) Architecture Assumptions
- Kubernetes cluster with NGINX Ingress
- Postgres as the primary state store (adjust if you use a different DB)
- Images hosted in GHCR
- DNS managed externally (e.g., Cloudflare or registrar)

## 2) Preparedness Checklist
- Multi-zone worker node pools (if supported by your cloud)
- Horizontal Pod Autoscaling (HPA) for stateless components
- Liveness/readiness probes set for all deployments
- Regular backups for:
  - PostgreSQL (daily full + optional WAL archiving)
  - Kubernetes ConfigMaps and Secrets (daily)
- Image registry redundancy (mirror critical images or cache)
- Documented credentials and least-privilege IAM

## 3) Backups

### 3.1 PostgreSQL backups
Use `k8s/backup/postgres-backup-cronjob.yaml` as a starting template. It creates a CronJob that runs `pg_dump` and uploads to S3-compatible storage.

- Provide env via a Secret with:
  - POSTGRES_HOST, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD
  - S3_ENDPOINT, S3_BUCKET, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

Validate restores weekly into a non-prod DB.

### 3.2 Cluster state backups
Use the provided PowerShell script `scripts/backup-k8s-resources.ps1` to export ConfigMaps and Secrets periodically.

Store backups in a private bucket with limited access and retention policies.

## 4) Recovery Procedures

### 4.1 Loss of a single node / partial outage
- Kubernetes will reschedule pods. Verify HPA and PDBs.
- Ensure ingress routes are healthy and TLS remains valid.

### 4.2 Database corruption / loss
1. Scale down apps that write to DB
2. Restore latest backup to a new Postgres instance
3. Update `k8s/02-secrets.yaml` to point apps to the restored instance
4. Roll out deployments
5. Validate basic flows and CI gate

### 4.3 Total cluster loss
1. Recreate cluster and node pools (multi-zone preferred)
2. Apply base manifests:
   - `k8s/00-namespace.yaml`
   - `k8s/00-nginx-*.yaml`
   - `k8s/00-cert-manager.yaml` and `k8s/cert-manager/cluster-issuer.yaml`
3. Restore DB from backups
4. Apply `k8s/02-secrets.yaml` and `k8s/01-configmap.yaml`
5. Deploy services: `k8s/03-postgresql.yaml` (if in-cluster), `k8s/04-backend.yaml`, `k8s/05-frontend.yaml`, `k8s/06-ingress.yaml`, `k8s/07-certificate.yaml`
6. Validate TLS and endpoint health

## 5) LLM Resilience and Fallbacks
- Domain triads defined in ConfigMap (primary, secondary, overwatch)
- Circuit breaker in chat service avoids repeatedly failing providers
- Keep multiple provider credentials ready; rotate keys if one is revoked

## 6) Testing DR
- Quarterly: simulate region failure (where feasible)
- Monthly: DB restore drill into staging
- Weekly: Randomly rotate LLM providers and validate triads continue to work

## 7) Contacts and Escalation
- On-call SRE / DevOps
- Security team for credential rotations and incident response

## 8) Appendix
- Example CronJob: `k8s/backup/postgres-backup-cronjob.yaml`
- Backup script: `scripts/backup-k8s-resources.ps1`
- TLS enablement: `docs/TLS_ENABLEMENT.md`
