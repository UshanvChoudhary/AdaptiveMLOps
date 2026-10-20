# AdaptiveMLOps — InsForge Database Schema Audit

**Date:** October 20, 2026  
**Target:** InsForge Cloud PostgreSQL Database (`insforge`)  
**Schema Status:** 100% RECONCILED (Zero Drift)  
**Alembic Revision:** `d87536722e30` (Head)  

---

## 1. Table and Column Inventory

Every table in the remote InsForge database was inspected and verified against the SQLAlchemy models in `backend/app/db/models/`.

### 1. `alembic_version`
- **Columns:** `version_num` (varchar, PK)
- **Current Head:** `d87536722e30`
- **Status:** Up to date.

### 2. `datasets`
- **Model:** `Dataset` in `backend/app/db/models/registry.py`
- **Columns:**
  - `id` (uuid, PK, nullable=NO)
  - `version` (varchar(50), unique, nullable=NO)
  - `checksum` (varchar(255), nullable=NO)
  - `created_at` (timestamp with time zone, nullable=YES)
- **Existing Rows:** 4

### 3. `training_runs`
- **Model:** `TrainingRun` in `backend/app/db/models/registry.py`
- **Columns:**
  - `id` (uuid, PK, nullable=NO)
  - `dataset_id` (uuid, FK -> `datasets.id`, nullable=NO)
  - `git_commit` (varchar, nullable=NO)
  - `hyperparameters` (json, nullable=NO)
  - `status` (varchar, nullable=NO)
  - `created_at` (timestamp with time zone, nullable=YES)
- **Existing Rows:** 4

### 4. `model_versions`
- **Model:** `ModelVersion` in `backend/app/db/models/registry.py`
- **Columns:**
  - `id` (uuid, PK, nullable=NO)
  - `version` (varchar, nullable=NO)
  - `algorithm` (varchar, nullable=NO)
  - `training_run_id` (uuid, FK -> `training_runs.id`, nullable=NO)
  - `artifact_path` (varchar, nullable=NO)
  - `status` (varchar, nullable=NO: `CANDIDATE`, `PRODUCTION`, `REJECTED`, `ARCHIVED`)
  - `created_at` (timestamp with time zone, nullable=YES)
- **Existing Rows:** 5

### 5. `evaluation_runs`
- **Model:** `EvaluationRun` in `backend/app/db/models/registry.py`
- **Columns:**
  - `id` (uuid, PK, nullable=NO)
  - `model_version_id` (uuid, FK -> `model_versions.id`, nullable=NO)
  - `dataset_id` (uuid, FK -> `datasets.id`, nullable=NO)
  - `metrics` (json, nullable=NO)
  - `created_at` (timestamp with time zone, nullable=YES)
- **Existing Rows:** 2

### 6. `predictions`
- **Model:** `Prediction` in `backend/app/db/models/prediction.py`
- **Columns:**
  - `id` (uuid, PK, nullable=NO)
  - `model_version` (varchar, nullable=NO)
  - `input_text` (text, nullable=NO)
  - `predicted_label` (varchar, nullable=NO)
  - `confidence` (double precision, nullable=NO)
  - `latency_ms` (double precision, nullable=NO)
  - `trace_id` (uuid, nullable=NO)
  - `created_at` (timestamp with time zone, nullable=YES)
- **Existing Rows:** 8

### 7. `feedback`
- **Model:** `Feedback` in `backend/app/db/models/feedback.py`
- **Columns:**
  - `id` (uuid, PK, nullable=NO)
  - `prediction_id` (uuid, FK -> `predictions.id`, nullable=NO)
  - `user_id` (varchar, nullable=YES)
  - `is_correct` (boolean, nullable=NO)
  - `corrected_label` (varchar, nullable=YES)
  - `comments` (text, nullable=YES)
  - `feedback_status` (varchar, nullable=NO: `NEW`, `USED_IN_TRAINING`, `IGNORED`)
  - `dataset_id` (uuid, FK -> `datasets.id`, nullable=YES)
  - `created_at` (timestamp with time zone, nullable=YES)
- **Existing Rows:** 3

### 8. `retraining_jobs`
- **Model:** `RetrainingJob` in `backend/app/db/models/retraining.py`
- **Columns:**
  - `id` (uuid, PK, nullable=NO)
  - `trigger_type` (varchar, nullable=NO: `MANUAL`, `SCHEDULED`, `THRESHOLD`, `DRIFT`)
  - `reason` (text, nullable=YES)
  - `feedback_count` (integer, nullable=NO)
  - `dataset_id` (uuid, FK -> `datasets.id`, nullable=YES)
  - `candidate_model_version_id` (uuid, FK -> `model_versions.id`, nullable=YES)
  - `status` (varchar, nullable=NO: `QUEUED`, `RUNNING`, `COMPLETED`, `FAILED`)
  - `error_message` (text, nullable=YES)
  - `started_at` (timestamp with time zone, nullable=YES)
  - `completed_at` (timestamp with time zone, nullable=YES)
  - `created_at` (timestamp with time zone, nullable=YES)
- **Existing Rows:** 6

### 9. `deployments`
- **Model:** `Deployment` in `backend/app/db/models/deployment.py`
- **Columns:**
  - `id` (uuid, PK, nullable=NO)
  - `model_version_id` (uuid, FK -> `model_versions.id`, nullable=NO)
  - `image_tag` (varchar, nullable=NO)
  - `environment` (varchar, nullable=NO)
  - `status` (varchar, nullable=YES: `PENDING`, `IN_PROGRESS`, `SUCCESS`, `FAILED`, `ROLLED_BACK`)
  - `actor` (varchar, nullable=YES)
  - `health_result` (json, nullable=YES)
  - `deployed_at` (timestamp with time zone, nullable=YES)
  - `created_at` (timestamp with time zone, nullable=YES)
- **Existing Rows:** 0 (Ready for production deployments)

### 10. `health_checks`
- **Model:** `HealthCheck` in `backend/app/db/models/deployment.py`
- **Columns:**
  - `id` (uuid, PK, nullable=NO)
  - `deployment_id` (uuid, FK -> `deployments.id`, nullable=NO)
  - `endpoint` (varchar, nullable=NO)
  - `status_code` (varchar, nullable=YES)
  - `response_time_ms` (varchar, nullable=YES)
  - `is_healthy` (boolean, nullable=NO)
  - `details` (text, nullable=YES)
  - `created_at` (timestamp with time zone, nullable=YES)
- **Existing Rows:** 0

### 11. `approvals`
- **Model:** `Approval` in `backend/app/db/models/governance.py`
- **Columns:**
  - `id` (uuid, PK, nullable=NO)
  - `model_version_id` (uuid, FK -> `model_versions.id`, nullable=NO)
  - `status` (enum `approvalstatus`: `PENDING`, `APPROVED`, `REJECTED`, nullable=NO)
  - `reviewer` (varchar, nullable=YES)
  - `comments` (text, nullable=YES)
  - `created_at` (timestamp without time zone, nullable=NO)
  - `updated_at` (timestamp without time zone, nullable=NO)
- **Existing Rows:** 0

### 12. `audit_logs`
- **Model:** `AuditLog` in `backend/app/db/models/governance.py`
- **Columns:**
  - `id` (uuid, PK, nullable=NO)
  - `action` (enum `auditaction`, nullable=NO)
  - `actor` (varchar, nullable=NO)
  - `resource_id` (uuid, nullable=YES)
  - `resource_type` (varchar, nullable=YES)
  - `details` (text, nullable=YES)
  - `created_at` (timestamp without time zone, nullable=NO)
- **Existing Rows:** 0

### 13. `model_audits`
- **Model:** `ModelAudit` in `backend/app/db/models/registry.py`
- **Columns:**
  - `id` (uuid, PK, nullable=NO)
  - `model_version_id` (uuid, FK -> `model_versions.id`, nullable=NO)
  - `action` (varchar, nullable=NO)
  - `reason` (varchar, nullable=YES)
  - `created_at` (timestamp with time zone, nullable=YES)
- **Existing Rows:** 3

### 14. `drift_runs`
- **Model:** `DriftRun` in `backend/app/db/models/monitoring.py`
- **Columns:**
  - `id` (uuid, PK, nullable=NO)
  - `drift_score` (double precision, nullable=NO)
  - `status` (enum `drift_status_enum`: `NORMAL`, `WARNING`, `CRITICAL`, nullable=NO)
  - `reference_dataset_id` (varchar, nullable=YES)
  - `current_window_start` (timestamp with time zone, nullable=YES)
  - `current_window_end` (timestamp with time zone, nullable=YES)
  - `class_distribution` (json, nullable=YES)
  - `confidence_trend` (json, nullable=YES)
  - `input_distribution` (json, nullable=YES)
  - `recommended_action` (varchar, nullable=YES)
  - `created_at` (timestamp with time zone, nullable=YES)
- **Existing Rows:** 0

---

## 2. Foreign Key Topology

All 12 foreign key constraints are established and active in PostgreSQL:

```
datasets (PK: id)
  ▲
  ├── training_runs.dataset_id
  ├── evaluation_runs.dataset_id
  ├── feedback.dataset_id
  └── retraining_jobs.dataset_id

training_runs (PK: id)
  ▲
  └── model_versions.training_run_id

model_versions (PK: id)
  ▲
  ├── evaluation_runs.model_version_id
  ├── model_audits.model_version_id
  ├── retraining_jobs.candidate_model_version_id
  ├── deployments.model_version_id
  └── approvals.model_version_id

predictions (PK: id)
  ▲
  └── feedback.prediction_id

deployments (PK: id)
  ▲
  └── health_checks.deployment_id
```

---

## 3. Schema Comparison and Reconciliation Verdict

- **SQLAlchemy Models:** 100% match with database tables and columns.
- **Alembic Revisions:** Remote database is at migration head `d87536722e30`.
- **Pre-existing Data:** Confirmed intact and preserved across all tables.
- **Verdict:** NO schema migrations required; existing schema is fully reconciled and production-ready.
