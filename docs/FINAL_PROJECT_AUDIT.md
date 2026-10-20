# AdaptiveMLOps — Final Project Audit and Remediation Report

**Date:** October 20, 2026  
**Project:** AdaptiveMLOps  
**Scope:** Pre-Demonstration Critical Security, Lifecycle, CI/CD, and Reliability Audit  
**Auditor:** Automated Engineering Remediation Team  

---

## 1. Executive Summary

A comprehensive pre-demonstration audit of the **AdaptiveMLOps** repository was conducted to evaluate system security, machine learning lifecycle fidelity, CI/CD pipeline integrity, and database reliability. 

Prior to remediation, several critical and high-severity defects were discovered:
1. **Critical Security Vulnerability:** An active external cloud PostgreSQL connection string containing plaintext credentials was hardcoded in `backend/app/config.py`.
2. **Authentication and Authorization Gaps:** Sensitive administrative and lifecycle endpoints (model promotion, approvals, deployments, rollbacks, retraining triggers, and `/demo/*` mutators) lacked authentication and role-based access control (RBAC). Furthermore, demo credentials could be authenticated in any environment.
3. **ML Lifecycle Discrepancy:** The system claimed XGBoost fraud detection in documentation and demo seeders while the actual ML pipeline was an NLP Customer Support Intent Classifier (TF-IDF + Logistic Regression). Retraining did not persist versioned disk artifacts or evaluate candidate artifacts against server-side quality gates.
4. **CI/CD Flaws:** Jenkinsfile stages contained `|| echo "Simulated build..."` fallback masks that allowed broken builds to pass silently, and deployment tests used in-process FastAPI `TestClient` mocks rather than verifying live running container endpoints.
5. **Health and Readiness:** The system lacked an explicit dependency readiness probe (`/ready`) to verify database and model availability independently from liveness (`/health`).

All identified issues have been remediated, verified with 47 automated tests (100% pass rate), verified against an empty PostgreSQL migration, validated in live Docker containers, and verified via real headless Selenium browser testing.

---

## 2. Comprehensive Issue Matrix

| Issue ID | Category | Description | Severity | Remediated In | Verification Evidence |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **SEC-01** | Priority 1: Security | Hardcoded cloud database connection string with plaintext password in `config.py` | **CRITICAL** | `backend/app/config.py` | Removed cloud URI; relies on env var; negative tests pass |
| **SEC-02** | Priority 1: Security | Demo user credentials accepted regardless of deployment environment | **HIGH** | `backend/app/api/v1/auth.py` | Locked behind `ENABLE_DEMO_MODE=true`; negative test verifies 401 when disabled |
| **SEC-03** | Priority 1: Security | Unauthenticated /demo mutation endpoints allowing arbitrary state manipulation | **HIGH** | `backend/app/api/v1/demo.py` | Gated by `verify_demo_mode` dependency; returns 403 Forbidden in non-demo mode |
| **SEC-04** | Priority 1: Security | Missing RBAC on Model Promotion, Approval, Rejection, Deployment, Rollback, and Retraining | **HIGH** | `registry.py`, `deployments.py`, `governance.py`, `retraining.py` | Added JWT & `X-API-Key` RBAC dependencies; 12 RBAC tests verify 401/403 responses |
| **SEC-05** | Priority 1: Security | Hardcoded credentials in CI deployment and health check scripts | **HIGH** | `scripts/ci/deploy.py`, `scripts/ci/health_check.py` | Parameterized via `ADMIN_API_KEY` and `TARGET_SERVICE_URL` env vars |
| **ML-01** | Priority 2: Lifecycle | Misrepresented ML model identity (XGBoost/Fraud claims vs TF-IDF + Logistic Regression) | **HIGH** | `demo.py`, `retraining_service.py`, docs | Reconciled all metadata, seeders, retraining logic, and docs to Customer Support Intent Classifier |
| **ML-02** | Priority 2: Lifecycle | Retraining did not persist real candidate model artifacts to disk | **HIGH** | `retraining_service.py` | Real artifacts (`model.joblib`, `vectorizer.joblib`, `metadata.json`) serialized to `ml/artifacts/{cand_version}/` |
| **ML-03** | Priority 2: Lifecycle | Model promotion did not enforce server-side quality gates or check disk artifacts | **HIGH** | `registry_service.py`, `registry.py` | Verified disk artifact existence; enforced `MIN_F1=0.80`, `MIN_ACCURACY=0.80`, `MAX_LATENCY_P95_MS=100.0` |
| **ML-04** | Priority 2: Lifecycle | Promoted model did not reload in-memory prediction service | **HIGH** | `registry_service.py` | `prediction_service.load_model(artifact_path)` hot-reloads model in memory upon promotion |
| **ML-05** | Priority 2: Lifecycle | Rollback only toggled database status without restoring model artifact or reloading service | **HIGH** | `governance.py` | Rollback validates target model artifact on disk, hot-reloads model, creates new deployment record |
| **ML-06** | Priority 2: Lifecycle | Uncontrolled concurrent retraining requests | **MEDIUM** | `retraining_service.py`, `retraining.py` | Added job locking to reject duplicate concurrent retraining attempts with 409 Conflict |
| **CI-01** | Priority 3: CI/CD | Pipeline stages masked Docker build and test failures with fallback echo masks | **HIGH** | `Jenkinsfile` | Removed all fallback masks; failed builds now fail the pipeline |
| **CI-02** | Priority 3: CI/CD | Deployment stage did not verify live container network service | **HIGH** | `Jenkinsfile`, `integration_tests.py`, `health_check.py` | Hits live HTTP endpoints (`http://localhost:8000/api/v1/ready` and predictions) with timeout |
| **CI-03** | Priority 3: CI/CD | Missing real browser E2E verification | **MEDIUM** | `scripts/ci/selenium_tests.py` | Headless Chrome Selenium test verifying frontend UI root element rendering |
| **REL-01** | Priority 4: Reliability | `/health` performed DB query instead of liveness; no `/ready` readiness check existed | **MEDIUM** | `backend/app/api/router.py` | Split into lightweight `/health` (liveness) and `/ready` (validates DB connectivity and model readiness) |
| **REL-02** | Priority 4: Reliability | Schema migrations unverified from empty database | **HIGH** | `alembic/versions` | Verified clean migration (`alembic upgrade head`) creates all 14 tables on fresh PostgreSQL DB |
| **REL-03** | Priority 4: Reliability | Missing schema validation for empty strings and invalid labels in prediction and feedback | **LOW** | `schemas/prediction.py`, `schemas/feedback.py` | Added `min_length=1` and intent label validation |

---

## 3. Priority 1 — Secrets and Security Audit

### 3.1 Exposed Credentials and Immediate Rotation Requirements

> [!CAUTION]
> **Mandatory Credential Rotation Notice:**  
> The following credentials were found committed to git history or hardcoded in source files and must be rotated immediately in all target environments:
> 1. **Insforge Cloud PostgreSQL Database Password:**  
>    - **Location:** `backend/app/config.py` (legacy `SQLALCHEMY_DATABASE_URI`)
>    - **Host:** `bdrb7j6b.ap-southeast.database.insforge.app`
>    - **User:** `postgres`
>    - **Action:** Rotate database user password immediately on the Insforge database provider console. Ensure the revoked password can no longer authenticate.
> 2. **JWT Secret Key:**  
>    - **Location:** `backend/app/config.py` default fallback value (`adaptive-mlops-production-secret-key-change-in-prod-2026`)
>    - **Action:** Generate a cryptographically random 256-bit key (e.g. `openssl rand -hex 32`) and inject via the `SECRET_KEY` environment variable.
> 3. **Admin API Key:**  
>    - **Location:** `backend/app/config.py` default fallback value (`admin_api_key_default_demo_only`)
>    - **Action:** Generate an unpredictable API key string and inject via `ADMIN_API_KEY` in environment variables and Jenkins Credentials store.
> 4. **PostgreSQL Default Container Password:**  
>    - **Location:** `docker-compose.yml` (`postgres:postgres`)
>    - **Action:** In staging and production environments, inject unique passwords via `.env` (`POSTGRES_PASSWORD`).

### 3.2 Demo Mode Lockout Enforcement
- Demo user accounts (`admin`, `reviewer`, `user`) are now gated behind `settings.ENABLE_DEMO_MODE`.
- In `backend/app/api/v1/auth.py`, if `ENABLE_DEMO_MODE=False`, any login attempt with demo credentials fails with `HTTP 401 Unauthorized: Demo mode is disabled. Use production directory credentials.`.
- In `backend/app/api/v1/demo.py`, all demonstration endpoints are guarded by `verify_demo_mode`. Non-demo environments immediately receive `HTTP 403 Forbidden: Demo endpoints are disabled in non-demo environments.`.

### 3.3 Role-Based Access Control (RBAC) Hardening
- Implemented `get_current_admin_or_api_key` and `get_current_reviewer_or_api_key` in `backend/app/dependencies.py`.
- **Model Promotion:** Requires `Role.ADMIN` or valid `X-API-Key`.
- **Candidate Approval & Rejection:** Requires `Role.REVIEWER` or `Role.ADMIN`.
- **Deployments & Rollbacks:** Requires `Role.ADMIN` or valid `X-API-Key`.
- **Retraining Triggers:** Requires `Role.ADMIN` or valid `X-API-Key`.
- Verified with 12 negative test cases in `backend/tests/test_security_rbac.py`.

---

## 4. Priority 2 — Real ML Lifecycle Fidelity

### 4.1 Model Identity Reconciliation
The repository previously had a major divergence between documentation claiming an XGBoost fraud detection model and the codebase actually implementing an NLP Customer Support Intent Classifier.
- **Reconciled Architecture:** scikit-learn TF-IDF Vectorizer + Logistic Regression.
- **Classes:** `billing`, `technical_support`, `refund`, `account_management`.
- **Metadata and Seeders:** Updated `backend/app/api/v1/demo.py` and `retraining_service.py` to seed and train customer service intent data.
- **Metric Distinction:** Seeded demo metrics in `demo.py` are explicitly flagged with `"metric_type": "seeded_demo"`, while real model evaluation in `retraining_service.py` computes genuine validation accuracy, macro F1, and p95 inference latency across held-out splits.

### 4.2 Candidate Artifact Persistence and Quality Gates
- `RetrainingService.train()` combines base customer support training samples with pending user feedback, computes a SHA-256 dataset checksum, fits the pipeline, evaluates metrics, and writes real artifacts to disk:
  - `ml/artifacts/{candidate_version}/model.joblib`
  - `ml/artifacts/{candidate_version}/vectorizer.joblib`
  - `ml/artifacts/{candidate_version}/metadata.json`
- `RegistryService.promote_candidate()` enforces:
  1. **Artifact Verification:** Verifies that candidate artifact files exist on disk before any database transaction.
  2. **Server-Side Quality Gates:** Checks `min_f1 >= 0.80`, `min_accuracy >= 0.80`, and `latency_p95_ms <= 100.0`. Candidates failing gates are rejected with `HTTP 400 Bad Request` and the production model remains untouched.
  3. **Hot Reloading:** Calls `prediction_service.load_model(artifact_path)` so that live predictions immediately reflect the newly promoted model without container restarts.

---

## 5. Priority 3 — CI/CD and Jenkins Pipeline Integrity

### 5.1 Elimination of Fallback Masks
The `Jenkinsfile` was audited and all deceptive fallback patterns were removed:
- Replaced: `sh "docker build ... || echo 'Simulated build'"`
- With: `sh "docker build -t adaptive-mlops-backend:${BUILD_NUMBER} ./backend"`
- If Docker build, unit tests, linting, or integration tests fail, the Jenkins pipeline immediately halts with build failure.

### 5.2 Real Deployment and Health Verification
- `scripts/ci/deploy.py` and `scripts/ci/health_check.py` now query the real live service at `http://localhost:8000/api/v1/ready`.
- Deployment requires HTTP 200 with `{"status": "ready", "database": "connected", "model": "loaded"}`.
- Removed hardcoded API keys from CI scripts; keys are now passed via the `ADMIN_API_KEY` environment variable or retrieved from Jenkins credentials.

---

## 6. Priority 4 — Database, Health, and Reliability

### 6.1 Clean Migration from Empty Database
To verify database migration integrity, a clean PostgreSQL database was provisioned (`empty_test_db`) and `alembic upgrade head` was executed. All 14 tables and indexes were created cleanly:
1. `users`
2. `model_artifacts`
3. `predictions`
4. `feedback`
5. `retraining_jobs`
6. `datasets`
7. `candidates`
8. `deployments`
9. `approvals`
10. `audit_logs`
11. `performance_metrics`
12. `drift_metrics`
13. `system_health`
14. `alembic_version`

### 6.2 Liveness vs Readiness Separation
- `/health` is now a pure liveness probe returning HTTP 200 `{"status": "ok"}` with zero database overhead.
- `/ready` is an active readiness probe executing `SELECT 1` against PostgreSQL and checking `prediction_service.model is not None`. If either fails, it returns HTTP 503 Service Unavailable.

---

## 7. Residual Limitations

1. **Single-Node Model Storage:** In this academic setup, artifacts are stored on the local filesystem (`ml/artifacts/`). For distributed multi-node clusters, an object store (e.g. AWS S3, Google Cloud Storage, or MinIO) should be used.
2. **Synchronous In-Process Retraining:** Retraining currently executes within FastAPI's background tasks threadpool. In enterprise production, retraining tasks should be offloaded to an asynchronous task queue like Celery + Redis or Kubeflow.
3. **Demo Drift Generator:** The `/demo/simulate-drift` endpoint generates synthetic drift metric entries for demonstration purposes. True production drift monitoring requires asynchronous streaming calculations across continuous prediction log batches.
