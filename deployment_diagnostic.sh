#!/bin/bash
# Deployment Status Check
# Run this to diagnose what's wrong with the topdog-ide.com deployment

echo "========================================="
echo "TopDog IDE - Deployment Diagnostic"
echo "========================================="
echo ""

# 1. Check if domain resolves
echo "[1] DNS Resolution Check"
echo "Testing: topdog-ide.com"
nslookup topdog-ide.com 2>/dev/null | grep -E "^Address|Name:" || echo "❌ Domain doesn't resolve"
echo ""

# 2. Check HTTP response
echo "[2] HTTP Connectivity Check"
echo "Testing: https://topdog-ide.com"
curl -I -k https://topdog-ide.com 2>/dev/null | head -5 || echo "❌ No HTTP response"
echo ""

# 3. Check API health
echo "[3] Backend API Health"
echo "Testing: https://topdog-ide.com/health"
curl -k https://topdog-ide.com/health 2>/dev/null | head -20 || echo "❌ API not responding"
echo ""

# 4. Check frontend
echo "[4] Frontend Load Test"
echo "Testing: https://topdog-ide.com/"
curl -k https://topdog-ide.com/ 2>/dev/null | head -20 || echo "❌ Frontend not loading"
echo ""

echo "========================================="
echo "Diagnostic Complete"
echo "========================================="
