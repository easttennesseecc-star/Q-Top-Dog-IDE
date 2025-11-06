#!/bin/sh
set -e

# Generate runtime env file for SPA
BACKEND_URL_VALUE="${BACKEND_URL:-http://api.topdog-ide.com}"
FRONTEND_URL_VALUE="${FRONTEND_URL:-http://topdog-ide.com}"
WORKSPACE_PROFILE_VALUE="${WORKSPACE_PROFILE:-}"
FEATURE_FLAGS_VALUE="${FEATURE_FLAGS:-}" # JSON string e.g. {"llm_overwatch":true}

cat > /app/dist/env.js <<EOF
window.__VITE_BACKEND_URL = '${BACKEND_URL_VALUE}';
window.__VITE_FRONTEND_URL = '${FRONTEND_URL_VALUE}';
window.__WORKSPACE_PROFILE = '${WORKSPACE_PROFILE_VALUE}';
try { window.__FEATURE_FLAGS = ${FEATURE_FLAGS_VALUE:-{}} } catch (e) { window.__FEATURE_FLAGS = {}; }
EOF

# Start static server
exec serve -s dist -l 3000 --single
