# TopDog IDE - UI Architecture with Medical/Compliance Features

## Current UI Structure (Assumed)
Based on a modern IDE, TopDog likely has:
- Left sidebar: File explorer, project nav
- Main editor: Code/visual editor
- Bottom panel: Terminal, output, logs
- Right sidebar: Properties, settings

## NEW UI ADDITIONS (Medical/Compliance Tiers)

### 1. NEW TOP-LEVEL TABS (Main Navigation)

When user is on TEAMS-MEDICAL, ENTERPRISE-MEDICAL, or PRO-MEDICAL tier:

```
┌─────────────────────────────────────────────────────────┐
│ CODE | AGENTS | COMPLIANCE | DATA-LINEAGE | EXPERIMENTS │
└─────────────────────────────────────────────────────────┘
     (existing)  (new)        (new)          (new)         (new)
```

**Tab 1: CODE** (existing)
- Traditional code editor
- File explorer
- Syntax highlighting
- Agent Marketplace integration

**Tab 2: AGENTS** (new for autonomous AI)
- Agent workflow builder
- Running agents dashboard
- Agent approval queue
- Agent audit log
- Agent marketplace browser

**Tab 3: COMPLIANCE** (new)
- HIPAA dashboard
- FDA 21 CFR Part 11 status
- GDPR DSAR requests
- Audit trail viewer
- Compliance reports
- PII detection alerts
- De-identification tools

**Tab 4: DATA-LINEAGE** (new)
- Data flow visualization (DAG/graph)
- Transformation tracking
- Source → Process → Output
- Version history per dataset
- Quality scoring

**Tab 5: EXPERIMENTS** (new for scientific)
- Active experiments list
- MLflow-style logging
- Metrics visualization
- Model registry
- Results comparison
- Reproducibility score
- Paper generation

---

## DETAILED UI LAYOUTS

### TAB: COMPLIANCE (For Medical Tiers)

```
┌──────────────────────────────────────────────────────────────────┐
│ COMPLIANCE DASHBOARD                                      [EXPORT] │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Status Overview                                                   │
│  ┌────────────────┬────────────────┬────────────────────────────┐ │
│  │ HIPAA: 95% ✅  │ FDA 21 CFR 11  │ GDPR: Compliant ✅         │ │
│  │ PII Detected: 0│ Status: READY  │ Last Audit: 3 days ago    │ │
│  └────────────────┴────────────────┴────────────────────────────┘ │
│                                                                    │
│  Recent Alerts                                                     │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ ⚠️  Agent accessed patient_data_2024 (3 mins ago)          │  │
│  │ ✅ Access logged & audit trail updated                    │  │
│  │                                                            │  │
│  │ ⚠️  De-identification quality score: 94% (excellent)      │  │
│  │ ✅ All PII masked successfully                            │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  Quick Actions                                                     │
│  [View Audit Trail] [Generate HIPAA Report] [GDPR DSAR Request]  │
│  [View PII Detections] [Run De-ID Check] [Compliance Cert]       │
│                                                                    │
├──────────────────────────────────────────────────────────────────┤
│  Detailed View: Switch Between                                     │
│  [HIPAA] [FDA 21 CFR 11] [GDPR] [SOC2] [Audit Trail] [Alerts]   │
└──────────────────────────────────────────────────────────────────┘
```

### TAB: DATA-LINEAGE (For Scientific Tiers)

```
┌──────────────────────────────────────────────────────────────────┐
│ DATA LINEAGE & TRANSFORMATIONS                           [EXPORT] │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Data Flow (Interactive DAG)                                       │
│                                                                    │
│          [Patient Data]                                           │
│               ↓                                                   │
│          [De-identification] ← Agent: privacy-mask-v2            │
│               ↓                                                   │
│          [Clean Dataset v2.1]                                    │
│               ↓                                                   │
│          [Feature Engineering] ← Agent: feature-extract-v1       │
│               ↓                                                   │
│          [ML Features v1.3]                                      │
│               ↓                                                   │
│          [LLM: Claude 3 Opus]                                    │
│               ↓                                                   │
│          [Predictions v1.0]                                      │
│               ↓                                                   │
│          [Clinical Decision Support]                             │
│                                                                    │
│  Right-click any node → View Details / Rollback / Compare        │
│                                                                    │
├──────────────────────────────────────────────────────────────────┤
│  Node Details Panel (Bottom)                                      │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ Clean Dataset v2.1                                         │  │
│  │ Created: 2024-11-01 14:32:15 UTC                          │  │
│  │ Source: [Patient Data] v1.0                               │  │
│  │ Transform: De-identification (privacy-mask-v2)            │  │
│  │ Records: 10,543 patients                                   │  │
│  │ Quality Score: 98.7%                                       │  │
│  │ Audit: Signed by john.smith@hospital.org                 │  │
│  │ [View Full Audit Trail] [Download Dataset] [Compare v2.0] │  │
│  └────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

### TAB: EXPERIMENTS (For Scientific Tiers)

```
┌──────────────────────────────────────────────────────────────────┐
│ EXPERIMENTS & RESULTS                                    [NEW EXP] │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Active Experiments                                                │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ ▶ Diagnosis Model v3.2 (running)                          │  │
│  │   Status: 45% complete (12 mins remaining)                │  │
│  │   Metrics: Accuracy 0.937, F1 0.891, Precision 0.923     │  │
│  │   [Stop] [Monitor] [Compare] [Generate Report]           │  │
│  │                                                            │  │
│  │ ✅ Treatment Optimization v2.1 (completed)               │  │
│  │   Status: Completed (2 hours ago)                        │  │
│  │   Metrics: AUC 0.956, Recall 0.911                       │  │
│  │   [View Results] [Compare] [Publish] [Reproduce]        │  │
│  │                                                            │  │
│  │ ❌ Feature Selection v1.0 (failed)                        │  │
│  │   Error: Out of memory on GPU                            │  │
│  │   [Retry with larger instance] [View Logs]              │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  Experiment Comparison                                             │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ Diagnosis Model v3.2 vs v3.1 vs v3.0                     │  │
│  │                                                            │  │
│  │ Metric          | v3.2    | v3.1    | v3.0    | Trend    │  │
│  │ ─────────────────┼─────────┼─────────┼─────────┼──────────│  │
│  │ Accuracy        | 0.937 ↑ | 0.931   | 0.921   | ↑ Better │  │
│  │ F1 Score        | 0.891   | 0.889   | 0.881   | ↑ Better │  │
│  │ Precision       | 0.923 ↓ | 0.927   | 0.925   | ↓ Worse  │  │
│  │ Recall          | 0.859 ↑ | 0.851   | 0.837   | ↑ Better │  │
│  │ AUC             | 0.956   | 0.952   | 0.941   | ↑ Better │  │
│  │                                                            │  │
│  │ [Analysis] [Generate Report] [Publish Paper] [Archive]   │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

### TAB: AGENTS (For Teams with Autonomy)

```
┌──────────────────────────────────────────────────────────────────┐
│ AUTONOMOUS AGENTS                                   [NEW AGENT] │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│  Running Agents                                                    │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ ▶ diagnosis-assistant (Medical Diagnosis)                │  │
│  │   Status: Active (processing)                            │  │
│  │   Currently: Analyzing patient case #4521                │  │
│  │   Last action: Read patient_data (10 mins ago) ✅ Audited│  │
│  │   Next action (requires approval): Suggest treatment     │  │
│  │   [Approve] [View Details] [Pause] [Terminate]          │  │
│  │                                                            │  │
│  │ ⏸  treatment-planner (Treatment Planning)                │  │
│  │   Status: Awaiting Approval                              │  │
│  │   Pending action: Modify patient 4521 treatment plan     │  │
│  │   [Approve] [Reject] [Modify] [View Justification]      │  │
│  │                                                            │  │
│  │ ✅ data-pipeline (Daily Data Ingestion)                  │  │
│  │   Status: Completed (1 day ago)                          │  │
│  │   Records processed: 2,543 patients                      │  │
│  │   [View Audit Trail] [Rerun]                            │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  Agent Approval Queue (Requires Human Decision)                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ 3 actions pending approval (2 require immediate attention) │  │
│  │                                                            │  │
│  │ [1] treatment-planner → Modify patient 4521 plan        │  │
│  │     Justification: "AUC 0.956, Recall 0.911 model"      │  │
│  │     [Approve] [Reject] [Request Change]                 │  │
│  │                                                            │  │
│  │ [2] diagnosis-assistant → Generate patient report        │  │
│  │     [Approve] [Reject] [Request Change]                 │  │
│  │                                                            │  │
│  │ [3] feature-engineer → Run experiment with new params    │  │
│  │     [Approve] [Reject] [Request Change]                 │  │
│  └────────────────────────────────────────────────────────────┘  │
│                                                                    │
│  Agent Marketplace                                                 │
│  [Browse Agents] [Upload Custom] [My Agents] [Revenue Share]     │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

---

## RIGHT SIDEBAR ADDITIONS (Properties Panel)

### For Medical Tiers

When a file/dataset is selected, right sidebar shows:

```
┌─────────────────────────────────┐
│ PROPERTIES                      │
├─────────────────────────────────┤
│                                 │
│ patient_data_2024.csv           │
│                                 │
│ FILE PROPERTIES                 │
│ • Size: 245 MB                  │
│ • Records: 10,543               │
│ • Modified: 3 hours ago         │
│                                 │
│ COMPLIANCE PROPERTIES ⭐         │
│ • Encryption: AES-256 ✅        │
│ • PII Status: 0 detected ✅     │
│ • De-ID Status: 98.7% ✅        │
│ • HIPAA Audit: ✅ Signed        │
│ • Access Log: 7 people          │
│                                 │
│ DATA LINEAGE                    │
│ • Source: Import 2024-11-01     │
│ • Transforms: 2 applied         │
│ • Version: 2.1 (latest)         │
│ • Previous: 2.0 (compare)       │
│                                 │
│ AUDIT TRAIL                     │
│ • Created by: john.smith        │
│ • Last modified by: agent-de-id │
│ • Signed: Yes ✅                │
│ [View Full Trail] [Export]      │
│                                 │
└─────────────────────────────────┘
```

---

## CONTEXT MENU ADDITIONS (Right-click)

For Medical/Scientific tiers, right-clicking a file/dataset shows:

```
Traditional Options:
├─ Cut
├─ Copy
├─ Paste
├─ Delete
├─ Rename
├─ Properties
│
NEW Medical/Science Options:
├─ [Compliance]
│  ├─ Check PII
│  ├─ Run De-identification
│  ├─ View Audit Trail
│  ├─ Export Compliance Report
│  └─ Share (with permissions)
├─ [Data]
│  ├─ View Lineage
│  ├─ Compare Versions
│  ├─ Restore Previous Version
│  └─ Tag Dataset (for experiment)
├─ [Experiments]
│  ├─ Use as Input
│  ├─ Compare with Experiment X
│  └─ Generate Reproducibility Report
└─ [Agents]
   ├─ Process with Agent
   └─ Schedule Agent Task
```

---

## BOTTOM PANEL ADDITIONS

### New "Audit Trail" Panel (For Medical/Compliance)

```
┌──────────────────────────────────────────────────────────────────┐
│ AUDIT TRAIL                                         [FILTER] [EXPORT]
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│ Timestamp          | User/Agent        | Action          | Status │
│ ────────────────────┼───────────────────┼─────────────────┼────── │
│ 2024-11-01 14:32:15| agent-de-id       | Modified dataset| ✅    │
│ 2024-11-01 14:30:00| john.smith        | Accessed data   | ✅    │
│ 2024-11-01 14:28:45| system            | Auto-backup     | ✅    │
│ 2024-11-01 14:20:12| agent-analyzer    | Read dataset    | ✅    │
│ 2024-11-01 14:15:30| jane.doe          | Approved action | ✅    │
│                                                                    │
│ All entries signed with cryptographic hash ✅                     │
│ Immutable audit trail (blockchain-style)                          │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

### New "Notifications" Panel (For Compliance Alerts)

```
┌──────────────────────────────────────────────────────────────────┐
│ COMPLIANCE NOTIFICATIONS                      [MARK ALL READ]    │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│ 🔴 URGENT                                                          │
│    Approval needed: treatment-planner wants to modify patient    │
│    Last 5 mins - [Approve] [Reject]                              │
│                                                                    │
│ 🟡 WARNING                                                         │
│    PII detected in export_2024.csv (5 instances)                 │
│    [View] [Auto De-ID] [Report]                                 │
│                                                                    │
│ 🟢 INFO                                                            │
│    Monthly HIPAA compliance audit completed: 98% compliant       │
│    [View Report] [Export for Stakeholders]                       │
│                                                                    │
│ 🔵 INFO                                                            │
│    Experiment "Diagnosis v3.2" completed successfully            │
│    Accuracy: 0.937 (+0.006 vs v3.1)                             │
│    [View Results] [Compare] [Publish]                            │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

---

## SETTINGS/PREFERENCES ADDITIONS

New section: "Compliance & Privacy Settings"

```
┌──────────────────────────────────────────────────────────────────┐
│ SETTINGS > COMPLIANCE & PRIVACY                                   │
├──────────────────────────────────────────────────────────────────┤
│                                                                    │
│ ENCRYPTION                                                         │
│ ☑ Enable HIPAA-grade encryption                                  │
│ ☑ AES-256 for data at rest                                       │
│ ☑ TLS 1.3 for data in transit                                    │
│                                                                    │
│ PII DETECTION                                                      │
│ ☑ Auto-detect PII (real-time)                                    │
│ ☑ Alert on PII in output                                         │
│ ☑ Block export if PII detected                                   │
│ ▼ Sensitivity: High (detect names, SSN, medical records)        │
│                                                                    │
│ AUDIT LOGGING                                                      │
│ ☑ Log all data access                                            │
│ ☑ Log all agent actions                                          │
│ ☑ Sign audit trail cryptographically                             │
│ ▼ Retention: 7 years (medical standard)                          │
│                                                                    │
│ APPROVAL WORKFLOWS                                                │
│ ☑ Require approval for: [Data modification] [De-identification]  │
│ ☑ Auto-approve: [Read-only operations] [Backups]                │
│ ▼ Approval timeout: 4 hours (escalate if not approved)           │
│                                                                    │
│ REGULATORY COMPLIANCE                                              │
│ ▼ Primary Regulation: HIPAA (can switch to GDPR, FDA, SOC2)     │
│ ☑ Generate monthly compliance reports                             │
│ ☑ Notify admins of compliance violations                         │
│                                                                    │
│                                                [SAVE] [RESET]     │
│                                                                    │
└──────────────────────────────────────────────────────────────────┘
```

---

## COMMAND PALETTE ADDITIONS

Users can press Ctrl+Shift+P to access new commands:

```
> compliance: generate hipaa report
> compliance: check pii
> compliance: view audit trail
> data: show lineage
> experiment: start new
> experiment: compare results
> agent: approve pending actions
> agent: view running agents
> audit: export trail
> hipaa: get certified status
```

---

## SUMMARY OF UI CHANGES

| Area | Change | Impact |
|------|--------|--------|
| Top Navigation | Add 4 new tabs (AGENTS, COMPLIANCE, DATA-LINEAGE, EXPERIMENTS) | Visible only for med/sci tiers |
| Right Sidebar | Add Compliance Properties section | Shows encryption, PII status, audit info |
| Bottom Panel | Add Audit Trail + Notifications panels | Always-visible audit logs |
| Context Menu | Add Compliance/Data/Experiment options | Right-click any file |
| Settings | Add Compliance section | Configure encryption, PII detection, approval |
| Status Bar | Add Compliance status indicator | Shows green/amber/red for compliance |

---

## TIER-SPECIFIC UI VISIBILITY

### FREE / PRO / PRO-PLUS (General Developers)
- Traditional IDE tabs only
- No compliance/audit/lineage tabs
- No agent approval queue
- No PII detection

### PRO-MEDICAL
- CODE tab (code editor)
- COMPLIANCE tab (HIPAA dashboard)
- Right sidebar: Compliance properties
- Settings: Compliance & Privacy

### TEAMS-SMALL / TEAMS-MEDIUM / TEAMS-LARGE (General)
- CODE + AGENTS tabs (agent builder)
- Approval queue for agent actions
- No compliance tab (unless TEAMS-MEDICAL)

### TEAMS-MEDICAL
- CODE + AGENTS + COMPLIANCE + EXPERIMENTS tabs
- Full audit trail
- Agent approval queue
- Medical-specific compliance dashboards

### ENTERPRISE-MEDICAL
- ALL tabs enabled
- Full regulatory compliance suite
- Advanced audit trails with digital signatures
- FDA-ready compliance interface

---

**UI remains clean & uncluttered for general developers, while medical/scientific users get powerful compliance & governance tools.**

**Status: ✅ UI ARCHITECTURE DESIGNED - Ready for frontend development**
