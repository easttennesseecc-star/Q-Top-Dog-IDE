#!/usr/bin/env bash
set -euo pipefail

# Args: <namespace> <service_name> [endpoint]
NS="${1:-}"
SVC="${2:-}"
EP="${3:-/health}"

if [[ -z "$NS" || -z "$SVC" ]]; then
  echo "Usage: $0 <namespace> <service_name> [endpoint]" >&2
  exit 2
fi

echo "[smoke] Namespace=$NS Service=$SVC Endpoint=$EP"

# Start port-forward
kubectl -n "$NS" port-forward svc/"$SVC" 18080:8000 >/tmp/pf.log 2>&1 &
PF_PID=$!

# Wait up to ~10s for port-forward to be ready
for i in {1..10}; do
  if curl -fsS --max-time 1 http://127.0.0.1:18080/ >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

# Query endpoint
RESP=$(curl -fsS --max-time 5 "http://127.0.0.1:18080${EP}" || true)

# Cleanup port-forward
kill "$PF_PID" 2>/dev/null || true
wait "$PF_PID" 2>/dev/null || true

if [[ -z "$RESP" ]]; then
  echo "[smoke] FAIL: empty response from ${EP}" >&2
  exit 1
fi

# Fast path: plain text OK/healthy/ready
if echo "$RESP" | grep -qiE '(^|[^a-z])(ok|healthy|ready)([^a-z]|$)'; then
  echo "[smoke] PASS: plaintext healthy signal"
  exit 0
fi

# Try JSON parsing using Python
python - "$RESP" <<'PY' || exit 1
import json, sys

data = sys.argv[1]
try:
    j = json.loads(data)
    if isinstance(j, dict):
        status = str(j.get('status') or j.get('ok') or j.get('healthy') or j.get('ready') or '').lower()
        if status in ('ok','healthy','ready','true','1'):
            print('[smoke] PASS: JSON dict healthy signal')
            sys.exit(0)
    if isinstance(j, list) and len(j) > 0:
        print('[smoke] PASS: non-empty JSON list')
        sys.exit(0)
    print('[smoke] FAIL: unexpected JSON shape')
    sys.exit(1)
except Exception as e:
    print('[smoke] FAIL: JSON parse error:', e)
    sys.exit(1)
PY
