# Roadmap: Medical Coding & Scientific Data

Goal: Deliver credible, compliant features for healthcare and research use‑cases while preserving speed and UX quality.

## Medical Coding Track

Scope
- PII/PHI Detection & Redaction (ingress + storage + egress)
- HIPAA security controls (encryption at rest/in transit, key mgmt, access logs)
- Audit Trails with E‑Signatures (FDA 21 CFR Part 11 framework)
- Consent & Data Governance (policies + enforcement hooks)

MVP (Phase 1)
- PII detection pipeline with redaction (regex + ML hybrid)
- Encryption at rest for DB + object storage; TLS 1.2+ everywhere
- Immutable audit log (append‑only) tied to user/session IDs
- Admin dashboards for audit review and access reports

Phase 2
- Digital signature workflows (hash + timestamp + signer identity)
- Fine‑grained access controls (record‑level, action‑level)
- Breach detection alerts + reporting templates

Engineering Notes
- Use KMS‑managed keys (or Vault) for envelope encryption
- Standardize event schema (actor, action, target, timestamp, signature)
- Add privacy test suite and data retention policies

## Scientific Data Track

Scope
- Data Lineage DAG (visual graph of data/artifact provenance)
- Experiment Tracking (MLflow or compatible)
- Dataset Versioning (hash‑based, metadata, diff and audit)
- Reproducibility Engine (containerized runs with pinned deps)

MVP (Phase 1)
- Integrate MLflow for experiments (runs, params, metrics, artifacts)
- Dataset registry with semantic metadata and version hashes
- Basic lineage graph linking datasets, runs, outputs

Phase 2
- Reproducibility runner (Kubernetes jobs + pinned images)
- Visual DAG editor and comparison views
- Export/import lineage (JSON + OCI artifact)

Engineering Notes
- Prefer open standards (MLflow, OpenLineage)
- Use object storage for large artifacts (DO Spaces)
- Add integrity checks (SHA‑256), retention policies, and access controls

## Compliance & Validation
- Threat modeling and data flow diagrams
- DPA/BAA readiness checklist
- Automated compliance tests (lint policies + unit/integration)
- Documentation and runbooks

## Dependencies
- Observability (logs/metrics/traces)
- Role‑based access control and policy engine
- Secure secret management
