# cert-manager manifests

- `cluster-issuer.yaml`: Create Let’s Encrypt staging and production ClusterIssuers.
- Use with NGINX Ingress. Ensure cert-manager controller and CRDs are installed (see `docs/DEPLOYMENT_TLS.md`).
