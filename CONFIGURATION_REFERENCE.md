# Configuration File for Database Setup

## Environment Variables (.env)

```bash
# ====================
# DATABASE CONFIG
# ====================
DB_HOST=localhost
DB_PORT=5432
DB_NAME=q_marketplace
DB_USER=postgres
DB_PASSWORD=your_secure_password_here

# ====================
# API CONFIG
# ====================
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=generate_a_random_string_here_minimum_32_chars

# ====================
# AUTH CONFIG
# ====================
JWT_SECRET=another_random_string_minimum_32_chars
JWT_EXPIRATION=86400  # 24 hours in seconds

# ====================
# AI PROVIDER KEYS (Optional - for startup initialization)
# ====================
# These are only loaded on startup, not exposed in dev
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
# GOOGLE_API_KEY=AIza...
# HUGGINGFACE_API_KEY=hf_...
# OLLAMA_URL=http://localhost:11434

# ====================
# SERVER CONFIG
# ====================
PORT=5000
HOST=0.0.0.0
WORKERS=4

# ====================
# LOGGING
# ====================
LOG_LEVEL=INFO
LOG_FILE=logs/marketplace.log

# ====================
# FEATURES
# ====================
ENABLE_AUDIT_LOG=true
ENABLE_RATE_LIMITING=true
MAX_REQUESTS_PER_HOUR=1000
ENABLE_REDIS_IDEMPOTENCY=false           # When true, idempotent responses stored in Redis (fallback in-memory)
IDEMPOTENCY_TTL_SECONDS=3600             # TTL for idempotent cache entries
ENABLE_REDIS_METRICS=false               # When true, core studio counters persisted in Redis for multi-instance durability
SAFETY_KEY_ROTATION_ENABLED=false        # Enables safety key rotation endpoints (/api/studio/safety-keys*)
SAFETY_KEY=dev-safety-key                # Fallback single safety key when rotation disabled
REDIS_URL=redis://localhost:6379/0       # Redis connection URL used for idempotency/metrics/rate limiting

# Marketplace mode (Directory vs Broker)
# Directory = BYOK only, no commissions, links to provider signup pages.
# Broker (legacy) = re-sell usage and bill through the platform.
MARKETPLACE_MODE=directory

# ====================
# DEPLOYMENT
# ====================
ENVIRONMENT=development  # development, staging, production
SENTRY_DSN=  # Error tracking

# ====================
# TOPDOG IDE SEGMENTS & PLANS (Observability & SLAs)
# ====================
# Controls for regulated domains and default labels used in Prometheus metrics.
# Headers can override these per-request (see below).
ENABLE_REGULATED_DOMAINS=true         # when true -> edition=regulated; else dev
DEFAULT_PLAN=Pro                      # Starter | Pro | Enterprise (used when header missing)
DEFAULT_DATA_SEGMENT=general          # general | medical | scientific (fallback)
DEFAULT_REGULATED_SEGMENT=medical     # default segment when edition=regulated
ENABLE_PROMETHEUS_METRICS=true        # Expose /api/studio/metrics/prometheus if client library available
PROMETHEUS_SCRAPE_PATH=/api/studio/metrics/prometheus # Path used by Prometheus server scrape config

# ====================
# STUDIO ORCHESTRATOR OBSERVABILITY (Micro-bench histograms)
# ====================
# The following metrics are emitted when Prometheus instrumentation is enabled:
# - studio_stage_execution_latency_seconds{stage_type,provider,outcome}
# - studio_stage_planning_latency_seconds{stage_type}
# - studio_credit_reservation_latency_seconds{provider,outcome}
# - studio_stage_success_total{stage_type,provider}
# - studio_stage_error_total{stage_type,provider}
# - studio_stage_fallback_total
# - studio_restricted_prompt_total
# - studio_moderation_severity_total{severity}
# Ensure Prometheus server scrape interval (e.g. 15s) is set appropriately for latency histograms.


# ====================
# LLM BOOTSTRAP (OPTIONAL)
# ====================
# Enable platform-managed provider keys to start without tenant BYOK.
# Prefer BYOK long-term for margins; use secrets manager in production.
PLATFORM_MANAGED_LLM_ENABLED=false
OPENAI_API_KEY=                       # set if using platform-managed OpenAI
ANTHROPIC_API_KEY=                    # set if using platform-managed Anthropic
GOOGLE_API_KEY=                       # optional
COHERE_API_KEY=                       # optional

# Spend guardrails for managed keys (per-tenant defaults; tune per plan)
SPEND_ALERT_TCU_WARN=200000
SPEND_ALERT_TCU_HARD=300000

# ====================
# PHONE PAIRING: SMS PROVIDERS (Optional)
# ====================
# Configure one provider for real SMS sends. If none configured, system runs in MOCK mode
# and logs SMS contents for development. See backend/services/sms_pairing_service.py.

# Twilio (recommended for easiest setup)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=+15551234567

# AWS SNS (alternative)
# Requires AWS credentials via environment/instance profile
# Region is taken from AWS configuration; set if needed:
# AWS_REGION=us-east-1
```

## Docker Compose (Optional - for local development)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:13-alpine
    container_name: q_marketplace_db
    environment:
      POSTGRES_USER: postgres
     APP_URL: Frontend application origin used by OAuth redirect flows. Set to http://localhost:5173 for local Vite dev.
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: q_marketplace_backend
    environment:
      DB_HOST: postgres
      DB_PORT: 5432
      DB_NAME: q_marketplace
      DB_USER: postgres
      DB_PASSWORD: postgres
      FLASK_ENV: production
    ports:
      - "5000:5000"
    depends_on:
    command: python backend/main.py

volumes:
  postgres_data:
```

Then start with:
```bash
docker-compose up -d
```

## TopDog IDE: Plan and Data Segment Labels

The backend emits Prometheus metrics labeled by customer plan and data segment.

- Request headers to set explicitly per-call:
  - `X-Plan`: Starter | Pro | Enterprise
  - `X-Data-Segment`: general | medical | scientific
- If headers are not present, defaults are taken from environment:
  - `DEFAULT_PLAN`, `DEFAULT_DATA_SEGMENT`; when `ENABLE_REGULATED_DOMAINS=true`, the segment falls back to `DEFAULT_REGULATED_SEGMENT`.

These labels appear on metrics like `CONSISTENCY_SCORE` and `HALLUCINATION_SEVERITY` to drive tier/segment-specific SLO alerts.

Example (PowerShell):

```powershell
Invoke-RestMethod -Method POST `
  -Uri http://localhost:8000/consistency/sli `
  -Headers @{ 'X-Plan'='Pro'; 'X-Data-Segment'='scientific' } `
  -Body (@{ score = 0.92 } | ConvertTo-Json) `
  -ContentType 'application/json'
```

Prometheus alert groups expect these labels and are defined under `observability/prometheus/alerts.yml` (e.g., `topdog-slo-gates-tiered`, `topdog-slo-gates-segments`).

## Safety Key Rotation

When `SAFETY_KEY_ROTATION_ENABLED=true` the studio routes expose endpoints:
- `GET /api/studio/safety-keys` list hashed keys (prefix only)
- `POST /api/studio/safety-keys` create new key (provide raw key_value; stored as sha256 hash)
- `POST /api/studio/safety-keys/rotate` atomically deactivates previous active keys and provisions new active
- `POST /api/studio/safety-keys/{id}/activate` toggle a key active
- `POST /api/studio/safety-keys/{id}/deactivate` deactivate a key

Validation precedence:
1. If rotation enabled and active keys exist -> hashed match required.
2. Else fallback to `SAFETY_KEY` environment value.

Restricted executions also require a prior disclaimer acknowledgment (`/api/studio/user/ack`).

## Idempotency & Metrics Durability

Environment flags:
- `ENABLE_REDIS_IDEMPOTENCY`: Store idempotent responses keyed by `X-Idempotency-Key`.
- `IDEMPOTENCY_TTL_SECONDS`: Expiration for cached execution payloads.
- `ENABLE_REDIS_METRICS`: Persist counters (e.g., stages_success, fallback_used_total) to Redis for multi-instance aggregation.

Redis keys namespace examples:
- `studio:idempotency:{key}` cached JSON response
- `studio:metrics:stages_success` global success counter
- `studio:metrics:moderation_severity_total:{severity}` severity buckets

## Error Taxonomy

Studio endpoints return `X-Error-Code` headers on failure (e.g., `STUDIO_PROMPT_TOO_SHORT`) to support client automation and structured retries.
Existing tests expect `detail` to remain a simple string; future global exception handler may wrap JSON body while preserving header semantics.

## Immutable Audit Chain

Executed stages append moderation/audit entries (`StudioAuditEntry`) with SHA256 `payload_hash` and `prev_hash` linking (`GENESIS` for first). Chain index increments per kind `execution_moderation`.
Tamper detection can be performed by verifying the linear hash linkage offline.

## Routing and Health Endpoints

- `/health` is registered before any catch-all routes and is excluded from compliance and canonical host redirects.
- Frontend SPA catch-all is registered after all API routers to avoid shadowing API paths (e.g., `/snapshots`, `/auth`, `/llm`, `/metrics`).
- Canonical redirect middleware skips internal/local hosts and never redirects paths prefixed with `/health`, `/metrics`, `/api`, `/ws`, `/_health`, `/readiness`, `/liveness`, or `/snapshots`.

Environment flags:
- `ENABLE_SNAPSHOT_API` (default: `true`) — toggles the snapshots API.
- `REQUIRE_SNAPSHOT_AUTH` (default: `false`) — when `true`, requires a valid `session_id` via query or `X-Session-Id` header for snapshot endpoints.

## Phone Pairing and SMS Invites

- Endpoints live under `/phone/*` (see `backend/routes/phone_pairing_api.py`).
- SMS pairing supports Twilio or AWS SNS. If neither is configured or libs are not installed,
  the service operates in MOCK mode and logs SMS to the server logs so you can test the flow.

Configure for production SMS:
- Install provider SDKs in the backend image: `twilio` (for Twilio) or `boto3` (for AWS SNS).
- Set the environment variables listed above (e.g., `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`).
- Expose a webhook for incoming SMS commands at `/phone/sms/webhook` (Twilio-compatible TwiML response).

## Docker Image (Optional - for production)

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ /app/backend/

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Run application
CMD ["python", "backend/main.py"]
```

Build with:
```bash
docker build -t q-marketplace:latest .
```

## requirements.txt

```
Flask==3.0.0
Flask-CORS==4.0.0
psycopg2-binary==2.9.9
python-dotenv==1.0.0
pytest==7.4.3
pytest-cov==4.1.0
requests==2.31.0
```

## Quick Start Scripts

### start-dev.sh (macOS/Linux)
```bash
#!/bin/bash

# Load environment
export $(cat .env | grep -v '^#' | xargs)

# Start PostgreSQL
echo "Starting PostgreSQL..."
sudo service postgresql start

# Run migration
echo "Running database migration..."
cd backend/database
python migrate.py
cd ../..

# Start backend
echo "Starting backend server..."
python backend/main.py
```

Make executable:
```bash
chmod +x start-dev.sh
./start-dev.sh
```

### start-dev.ps1 (Windows)
```powershell
# Load environment
Get-Content .env | ForEach-Object {
    if ($_ -notmatch '^#' -and $_ -match '=') {
        $name, $value = $_.Split('=')
        [Environment]::SetEnvironmentVariable($name, $value)
    }
}

# Start PostgreSQL (assumes installed)
Write-Host "Starting PostgreSQL..."
# Adjust path based on your PostgreSQL installation
& "C:\Program Files\PostgreSQL\13\bin\psql.exe" -U postgres -c "SELECT 1"

# Run migration
Write-Host "Running database migration..."
Set-Location backend/database
python migrate.py
Set-Location ../..

# Start backend
Write-Host "Starting backend server..."
python backend/main.py
```

## Health Check Script

Create `health_check.sh`:

```bash
#!/bin/bash

echo "🔍 Health Check for Q Marketplace"
echo "=================================="

# Check PostgreSQL
echo -n "PostgreSQL: "
if pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "✅ Connected"
else
    echo "❌ Not responding"
    exit 1
fi

# Check Backend
echo -n "Backend API: "
if curl -s http://localhost:5000/health > /dev/null 2>&1; then
    echo "✅ Running"
else
    echo "❌ Not responding"
    exit 1
fi

# Check Database Schema
echo -n "Schema: "
TABLES=$(psql -U postgres -d q_marketplace -tc "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public'")
if [ "$TABLES" -ge 10 ]; then
    echo "✅ Complete ($TABLES tables)"
else
    echo "❌ Incomplete ($TABLES tables)"
    exit 1
fi

echo ""
echo "✅ All systems operational!"
```

## Monitoring Configuration

Create `monitoring.yaml`:

```yaml
# Prometheus metrics
metrics:
  enabled: true
  port: 9090
  path: /metrics

# Key metrics to track
tracked_metrics:
  - api_request_count
  - api_response_time
  - database_connection_pool
  - user_balance_total
  - transaction_volume
  - chat_message_count
  - model_usage_frequency
  - error_rate

# Alerts
alerts:
  - name: HighErrorRate
    condition: error_rate > 0.05
    action: notify_slack

  - name: DatabaseConnectivity
    condition: db_response_time > 5000
    action: alert_oncall

  - name: LowBalance
    condition: user.balance < 10.0
    action: email_user
```

## Backup Configuration

Create `backup-schedule.sh`:

```bash
#!/bin/bash

BACKUP_DIR="/backups/q_marketplace"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="q_marketplace"
DB_USER="postgres"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Daily backup
pg_dump -U $DB_USER $DB_NAME | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# Keep only last 30 days
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +30 -delete

# Verify backup
if [ -f "$BACKUP_DIR/backup_$DATE.sql.gz" ]; then
    echo "✅ Backup created: backup_$DATE.sql.gz"
else
    echo "❌ Backup failed"
    exit 1
fi
```

Schedule with cron:
```bash
# Run daily at 2 AM
0 2 * * * /path/to/backup-schedule.sh
```

## Deployment Checklist

```markdown
## Pre-Deployment
- [ ] All tests passing locally (pytest)
- [ ] Database migration successful
- [ ] Environment variables configured
- [ ] Secrets not committed to Git
- [ ] Code reviewed and approved
- [ ] Documentation updated

## Deployment to Staging
- [ ] Create staging database
- [ ] Run migration on staging
- [ ] Deploy backend code
- [ ] Deploy frontend code
- [ ] Run E2E tests
- [ ] Check logs for errors
- [ ] Monitor error rate

## Deployment to Production
- [ ] Database backup created
- [ ] Load balancer configured
- [ ] SSL certificates ready
- [ ] Monitoring configured
- [ ] On-call rotation confirmed
- [ ] Rollback plan ready
- [ ] Deploy during low traffic
- [ ] Verify all endpoints
- [ ] Monitor for 1 hour

## Post-Deployment
- [ ] Check application logs
- [ ] Verify database integrity
- [ ] Monitor resource usage
- [ ] Check error rates
- [ ] Confirm users can sign up
- [ ] Verify transactions working
```

## Security Checklist

```markdown
## Database Security
- [ ] Change default PostgreSQL password
- [ ] Enable SSL connections
- [ ] Configure network firewall
- [ ] Enable audit logging
- [ ] Regular backups tested
- [ ] Rotation of encryption keys
- [ ] Monitoring of failed logins

## Application Security
- [ ] Secrets in environment variables only
- [ ] HTTPS enabled
- [ ] CORS configured properly
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention (parameterized queries)
- [ ] Regular security updates

## Operational Security
- [ ] SSH keys for deployment
- [ ] Encrypted backups
- [ ] Access logs monitored
- [ ] Incident response plan
- [ ] Security training for team
- [ ] Regular security audits
```

## Troubleshooting

### Database Connection Issues
```bash
# Test connection
psql -h localhost -U postgres -d q_marketplace -c "SELECT 1"

# Check status
pg_isready -h localhost -p 5432

# View logs
tail -f /var/log/postgresql/postgresql.log
```

### Migration Failed
```bash
# Rerun migration
python backend/database/migrate.py

# Or manually reset (CAUTION - deletes data)
psql -U postgres -c "DROP DATABASE q_marketplace"
python backend/database/migrate.py
```

### API Not Responding
```bash
# Check logs
tail -f logs/marketplace.log

# Test endpoint
curl -X GET http://localhost:5000/health

# Check port in use
lsof -i :5000
```

---

**Everything configured. Ready to deploy!** 🚀
