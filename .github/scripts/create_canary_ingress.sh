#!/usr/bin/env bash
set -euo pipefail
NS="$1"          # namespace
RELEASE_NAME="$2" # release (topdog-canary | topdog-green)
HOSTS_CSV="$3"   # comma separated hosts
WEIGHT="$4"      # canary weight

SERVICE_NAME="${RELEASE_NAME}-topdog"
IFS=',' read -ra HOSTS <<< "${HOSTS_CSV}"
IDX=0
for H in "${HOSTS[@]}"; do
  NAME="canary-ingress-${IDX}"
  cat <<EOF | kubectl -n "${NS}" apply -f -
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ${NAME}
  annotations:
    kubernetes.io/ingress.class: nginx
    nginx.ingress.kubernetes.io/canary: "true"
    nginx.ingress.kubernetes.io/canary-weight: "${WEIGHT}"
spec:
  ingressClassName: nginx
  rules:
  - host: ${H}
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ${SERVICE_NAME}
            port:
              number: 8000
EOF
  IDX=$((IDX+1))
done
