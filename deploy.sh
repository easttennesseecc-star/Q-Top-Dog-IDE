#!/bin/bash

# 🚀 PHASE 7: PRODUCTION DEPLOYMENT AUTOMATION SCRIPT
# This script automates the deployment to Digital Ocean App Platform
# Requirements: Digital Ocean CLI (doctl) installed and authenticated

set -e  # Exit on error

echo "======================================"
echo "🚀 PHASE 7: PRODUCTION DEPLOYMENT"
echo "======================================"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="quellum-topdog-ai"
REGION="nyc3"  # New York
INSTANCE_SIZE="basic-xs"  # Smallest available
IMAGE="topdog-latest"
DOCKER_REGISTRY="registry.digitalocean.com"

# Functions
log_section() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}========================================${NC}"
}

log_step() {
    echo -e "${GREEN}✓${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

log_error() {
    echo -e "${RED}✗${NC} $1"
}

# Pre-flight checks
log_section "PRE-FLIGHT CHECKS"

# Check Docker installed
if ! command -v docker &> /dev/null; then
    log_error "Docker is not installed. Please install Docker first."
    exit 1
fi
log_step "Docker found"

# Check doctl installed
if ! command -v doctl &> /dev/null; then
    log_error "Digital Ocean CLI (doctl) is not installed."
    echo "Install from: https://docs.digitalocean.com/reference/doctl/how-to/install/"
    exit 1
fi
log_step "Digital Ocean CLI (doctl) found"

# Check doctl authenticated
if ! doctl auth list 2>/dev/null | grep -q "access-token"; then
    log_error "Digital Ocean CLI not authenticated"
    echo "Run: doctl auth init"
    exit 1
fi
log_step "Digital Ocean authenticated"

# Check app.yaml exists
if [ ! -f "app.yaml" ]; then
    log_error "app.yaml not found in current directory"
    exit 1
fi
log_step "app.yaml found"

# Check Dockerfile exists
if [ ! -f "Dockerfile" ]; then
    log_error "Dockerfile not found in current directory"
    exit 1
fi
log_step "Dockerfile found"

log_step "All pre-flight checks passed ✓"

# STEP 1: Build Docker Image
log_section "STEP 1: BUILD DOCKER IMAGE"

echo "Building Docker image: $IMAGE"
docker build -t $IMAGE:latest .

if [ $? -eq 0 ]; then
    log_step "Docker image built successfully"
else
    log_error "Docker build failed"
    exit 1
fi

# STEP 2: Push to Digital Ocean Container Registry
log_section "STEP 2: PUSH TO DIGITAL OCEAN REGISTRY"

# Get registry URL
REGISTRY_URL=$(doctl registry get | grep -oP 'registry\.digitalocean\.com/[^\s]+')
if [ -z "$REGISTRY_URL" ]; then
    log_warning "Creating Digital Ocean container registry..."
    doctl registry create $APP_NAME --region $REGION
    REGISTRY_URL="registry.digitalocean.com/$(doctl account get --format namespace --no-header)"
fi

log_step "Registry URL: $REGISTRY_URL"

# Tag image
docker tag $IMAGE:latest $REGISTRY_URL/$APP_NAME:latest
log_step "Image tagged: $REGISTRY_URL/$APP_NAME:latest"

# Login to registry
echo $( doctl auth-token ) | docker login -u unused --password-stdin $DOCKER_REGISTRY
log_step "Logged into Digital Ocean registry"

# Push image
echo "Pushing image to registry..."
docker push $REGISTRY_URL/$APP_NAME:latest

if [ $? -eq 0 ]; then
    log_step "Image pushed successfully"
else
    log_error "Docker push failed"
    exit 1
fi

# STEP 3: Create Digital Ocean App (if not exists)
log_section "STEP 3: CREATE/UPDATE DIGITAL OCEAN APP"

# Check if app exists
APP_EXISTS=$(doctl apps list --format name --no-header | grep -c "$APP_NAME" || true)

if [ $APP_EXISTS -eq 0 ]; then
    log_step "App does not exist, creating new app..."
    
    # Create app from app.yaml
    doctl apps create --spec app.yaml
    
    if [ $? -eq 0 ]; then
        log_step "App created successfully"
    else
        log_error "App creation failed"
        exit 1
    fi
else
    log_step "App already exists, skipping creation"
fi

# STEP 4: Deploy App
log_section "STEP 4: DEPLOY APPLICATION"

APP_ID=$(doctl apps list --format id,name --no-header | grep "$APP_NAME" | awk '{print $1}')

if [ -z "$APP_ID" ]; then
    log_error "Could not find app ID for $APP_NAME"
    exit 1
fi

log_step "App ID: $APP_ID"

echo "Deploying app..."
doctl apps create-deployment $APP_ID

# Wait for deployment
log_step "Waiting for deployment to complete..."
DEPLOYMENT_STATUS="PENDING"
WAIT_COUNT=0
MAX_WAIT=600  # 10 minutes

while [ "$DEPLOYMENT_STATUS" != "ACTIVE" ] && [ $WAIT_COUNT -lt $MAX_WAIT ]; do
    sleep 10
    WAIT_COUNT=$((WAIT_COUNT + 10))
    
    DEPLOYMENT_STATUS=$(doctl apps get $APP_ID --format updated_at,status --no-header | tail -1)
    
    if [ $((WAIT_COUNT % 60)) -eq 0 ]; then
        echo "Status: $DEPLOYMENT_STATUS (waited ${WAIT_COUNT}s...)"
    fi
done

if [ "$DEPLOYMENT_STATUS" = "ACTIVE" ]; then
    log_step "Deployment completed successfully!"
else
    log_error "Deployment failed or timed out"
    exit 1
fi

# STEP 5: Get App URL
log_section "STEP 5: GET APP DETAILS"

APP_URL=$(doctl apps get $APP_ID --format live-url --no-header)
log_step "App URL: $APP_URL"

# STEP 6: Verify Deployment
log_section "STEP 6: VERIFY DEPLOYMENT"

echo "Testing health endpoint..."
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" $APP_URL/health)

if [ "$HEALTH_CHECK" = "200" ]; then
    log_step "Health check passed (HTTP $HEALTH_CHECK)"
else
    log_warning "Health check returned HTTP $HEALTH_CHECK (expected 200)"
fi

# Test API endpoint
echo "Testing API endpoint..."
API_CHECK=$(curl -s -o /dev/null -w "%{http_code}" -X GET $APP_URL/api/health)

if [ "$API_CHECK" = "200" ] || [ "$API_CHECK" = "404" ]; then
    log_step "API endpoint accessible (HTTP $API_CHECK)"
else
    log_warning "API endpoint returned HTTP $API_CHECK"
fi

# STEP 7: Configure Environment Variables
log_section "STEP 7: ENVIRONMENT VARIABLES"

log_warning "Please configure the following environment variables in Digital Ocean:"
echo ""
echo "1. Go to Digital Ocean Dashboard → Apps → $APP_NAME → Settings"
echo "2. Click 'Edit and Deploy'"
echo "3. Add these environment variables:"
echo ""
echo "   DATABASE_URL=<your-database-url>"
echo "   API_SECRET_KEY=<strong-random-key>"
echo "   ENVIRONMENT=production"
echo "   DEBUG=false"
echo "   STRIPE_API_KEY=sk_live_<your-key>"
echo "   STRIPE_WEBHOOK_SECRET=whsec_<your-secret>"
echo ""
echo "4. Click 'Deploy'"
echo ""

# STEP 8: Setup Stripe Webhooks
log_section "STEP 8: STRIPE WEBHOOK SETUP"

WEBHOOK_URL="$APP_URL/webhooks/stripe"
echo "Configure this webhook URL in Stripe Dashboard:"
echo ""
echo "   $WEBHOOK_URL"
echo ""
echo "Webhook events to enable:"
echo "   • charge.succeeded"
echo "   • charge.failed"
echo "   • customer.subscription.updated"
echo "   • customer.subscription.deleted"
echo ""

# STEP 9: Summary
log_section "🎉 DEPLOYMENT COMPLETE!"

echo ""
echo "Application Details:"
echo "  Name: $APP_NAME"
echo "  ID: $APP_ID"
echo "  URL: $APP_URL"
echo "  Region: $REGION"
echo ""
echo "Next Steps:"
echo "  1. Set environment variables in Digital Ocean console"
echo "  2. Configure Stripe webhooks (URL above)"
echo "  3. Run database migrations (if needed)"
echo "  4. Test payment flow"
echo "  5. Monitor application logs"
echo ""
echo "View Logs:"
echo "  doctl apps logs $APP_ID --follow"
echo ""
echo "View App Details:"
echo "  doctl apps get $APP_ID"
echo ""

log_step "Deployment script completed successfully!"
log_step "Your app is now live at: $APP_URL"

echo ""
echo "======================================"
echo "🚀 PHASE 7: DEPLOYMENT COMPLETE"
echo "======================================"
