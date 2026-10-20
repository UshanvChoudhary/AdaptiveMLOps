# AdaptiveMLOps — Final Verification Results

**Date:** October 20, 2026  
**Status:** ALL TESTS AND VERIFICATIONS PASSED (100%)  
**Environments:** 
- Remote: InsForge Managed PostgreSQL 15 (TLS/SSL Require)
- Local: Docker Engine (FastAPI, React + Vite, PostgreSQL 15)
- Automated Test Suite: Dedicated Isolated SQLite In-Memory Engine (`conftest.py`)

---

## 1. Summary of Verification Runs

Every command listed in this document was executed locally against the actual codebase and running infrastructure. No mocked or simulated build outputs are accepted as evidence.

| Verification Step | Exact Command Executed | Exit Code | Actual Result | Blockers |
| :--- | :--- | :--- | :--- | :--- |
| **InsForge DB Connectivity** | `python scratch/test_insforge_conn.py` | `0` | **Connected (SELECT 1: True, PG 15.18, 14 tables)** | None |
| **InsForge Schema Reconciliation** | `python scratch/inspect_insforge_details.py` | `0` | **100% matched models, 12 FKs valid, 0 schema drift** | None |
| **InsForge Real Data Persistence** | `python scratch/test_insforge_persistence.py` | `0` | **Prediction, feedback, deployment, health, approval, audit persisted & cleaned** | None |
| **Isolated Backend Test Suite** | `python -m pytest backend/tests` | `0` | **47 passed in 7.68s (isolated from InsForge)** | None |
| **Negative Scenarios Suite** | `python -m pytest backend/tests/test_negative_scenarios.py -v` | `0` | **10 passed in 1.93s** | None |
| **Security & RBAC Suite** | `python -m pytest backend/tests/test_security_rbac.py -v` | `0` | **12 passed in 1.93s** | None |
| **Docker Compose Config** | `docker-compose config` | `0` | **Valid YAML configuration with env parameterization** | None |
| **Docker Build Backend** | `docker build -t adaptive-mlops-backend:test ./backend` | `0` | **Built successfully without fallback masks** | None |
| **Docker Build Frontend** | `docker build -t adaptive-mlops-frontend:test ./frontend` | `0` | **Built successfully** | None |
| **Frontend Linting** | `cd frontend && npm run lint` | `0` | **0 errors (9 minor warnings)** | None |
| **Frontend TypeScript Build** | `cd frontend && npm run build` | `0` | **Built in 272ms with 0 errors** | None |
| **Live API Integration Test** | `python scripts/ci/integration_tests.py` | `0` | **Passed against running service on port 8000** | None |
| **Real Selenium Browser E2E** | `python scripts/ci/selenium_tests.py` | `0` | **Passed against running frontend on port 5173** | None |

---

## 2. InsForge Database Connectivity and Schema Verification

### Connectivity Test (`python scratch/test_insforge_conn.py`)
```
Connectivity check (SELECT 1): True
Current Database: insforge
PostgreSQL Version: PostgreSQL 15.18 (Debian 15.18-1.pgdg13+1) on aarch64-unknown-linux-gnu
Existing public tables (14): ['alembic_version', 'approvals', 'audit_logs', 'datasets', 'deployments', 'drift_runs', 'evaluation_runs', 'feedback', 'health_checks', 'model_audits', 'model_versions', 'predictions', 'retraining_jobs', 'training_runs']
Alembic version in remote DB: ['d87536722e30']
Connection closed successfully.
Exit Code: 0
```

### Schema Audit Summary (`docs/DATABASE_SCHEMA_AUDIT.md`)
- All 14 application tables match their respective SQLAlchemy declarations in `backend/app/db/models/`.
- All 12 foreign key constraints are established and active.
- Existing records (4 datasets, 4 training runs, 5 model versions, 8 predictions, 3 feedback records, 6 retraining jobs) are preserved intact.
- Alembic migration version on InsForge is at head (`d87536722e30`). Zero destructive migrations required.

---

## 3. Real Data Persistence Verification (`python scratch/test_insforge_persistence.py`)

A full transactional test was executed directly against the remote InsForge database:

```
=== BEGINNING REAL DATA PERSISTENCE VERIFICATION ON INSFORGE ===
[OK] Found existing champion model version in InsForge: v1.0.0 (id=9e497ca5-df85-4cb4-ad6c-6ee646171525)
[OK] Test prediction persisted to InsForge PostgreSQL (id=45105834-a2af-4bc8-bf42-5c632212aaa4)
[OK] Linked feedback record persisted with foreign key (id=ddf826be-8c84-4849-befe-a717add01182)
[OK] Verified prediction and feedback retrieval and field integrity
[OK] Deployment, HealthCheck, Approval, and AuditLog records successfully persisted
[OK] Verified all records retrieved successfully with complete constraint integrity

Cleaning up test records (preserving all production records)...
[OK] Test records cleaned up cleanly without affecting existing database state
[OK] Pre-existing state preserved: 8 predictions, 5 model versions intact
=== INSFORGE PERSISTENCE VERIFICATION COMPLETED SUCCESSFULLY ===
Exit Code: 0
```

---

## 4. Priority Negative Scenarios Verification

Executed in `backend/tests/test_negative_scenarios.py`:

```
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
collected 10 items

backend/tests/test_negative_scenarios.py::test_negative_invalid_login PASSED [ 10%]
backend/tests/test_negative_scenarios.py::test_negative_unauthenticated_promotion_attempt PASSED [ 20%]
backend/tests/test_negative_scenarios.py::test_negative_user_attempting_admin_actions PASSED [ 30%]
backend/tests/test_negative_scenarios.py::test_negative_bad_challenger_rejected PASSED [ 40%]
backend/tests/test_negative_scenarios.py::test_negative_missing_model_artifact PASSED [ 50%]
backend/tests/test_negative_scenarios.py::test_negative_database_unavailable PASSED [ 60%]
backend/tests/test_negative_scenarios.py::test_negative_training_job_failure PASSED [ 70%]
backend/tests/test_negative_scenarios.py::test_negative_deployment_health_check_failure PASSED [ 80%]
backend/tests/test_negative_scenarios.py::test_negative_rollback_after_failed_deployment PASSED [ 90%]
backend/tests/test_negative_scenarios.py::test_negative_drift_alert_without_automatic_deployment PASSED [100%]

============================= 10 passed in 1.93s ==============================
```

---

## 5. Security and RBAC Test Suite Verification

Executed in `backend/tests/test_security_rbac.py`:

```
============================= test session starts =============================
collected 12 items

backend/tests/test_security_rbac.py::test_demo_mode_disabled_blocks_demo_login PASSED [  8%]
backend/tests/test_security_rbac.py::test_demo_mode_disabled_blocks_demo_endpoints PASSED [ 16%]
backend/tests/test_security_rbac.py::test_unauthenticated_promote_rejected PASSED [ 25%]
backend/tests/test_security_rbac.py::test_user_role_promote_forbidden PASSED [ 33%]
backend/tests/test_security_rbac.py::test_admin_role_promote_allowed PASSED [ 41%]
backend/tests/test_security_rbac.py::test_api_key_promote_allowed PASSED [ 50%]
backend/tests/test_security_rbac.py::test_unauthenticated_deploy_rejected PASSED [ 58%]
backend/tests/test_security_rbac.py::test_user_deploy_forbidden PASSED [ 66%]
backend/tests/test_security_rbac.py::test_unauthenticated_retraining_trigger_rejected PASSED [ 75%]
backend/tests/test_security_rbac.py::test_user_retraining_trigger_forbidden PASSED [ 83%]
backend/tests/test_security_rbac.py::test_unauthenticated_rollback_rejected PASSED [ 91%]
backend/tests/test_security_rbac.py::test_user_rollback_forbidden PASSED [100%]

============================= 12 passed in 1.93s ==============================
```

---

## 6. Full Pytest Suite Verification (Isolated Environment)

```
PS C:\Users\USER\Desktop\Programs\adaptive-mlops> python -m pytest backend/tests
============================= test session starts =============================
platform win32 -- Python 3.14.6, pytest-9.1.1, pluggy-1.6.0
rootdir: C:\Users\USER\Desktop\Programs\adaptive-mlops\backend
configfile: pytest.ini
plugins: anyio-4.15.1, asyncio-1.4.0, cov-7.1.0
collected 47 items

backend/tests/test_feedback.py ......                                    [ 12%]
backend/tests/test_health.py ..                                          [ 17%]
backend/tests/test_ml.py ....                                            [ 25%]
backend/tests/test_negative_scenarios.py ..........                      [ 46%]
backend/tests/test_predictions.py ......                                 [ 59%]
backend/tests/test_registry.py ...                                       [ 65%]
backend/tests/test_retraining.py ....                                    [ 74%]
backend/tests/test_security_rbac.py ............                         [100%]

======================= 47 passed, 8 warnings in 7.68s ========================
```

---

## 7. Docker and Frontend Builds Verification

### Backend Docker Build
```
PS C:\Users\USER\Desktop\Programs\adaptive-mlops> docker build -t adaptive-mlops-backend:test ./backend
#13 exporting to image
#13 naming to docker.io/library/adaptive-mlops-backend:test done
Exit Code: 0
```

### Frontend Docker Build
```
PS C:\Users\USER\Desktop\Programs\adaptive-mlops> docker build -t adaptive-mlops-frontend:test ./frontend
#11 exporting to image
#11 naming to docker.io/library/adaptive-mlops-frontend:test done
Exit Code: 0
```

### Frontend TypeScript Build
```
PS C:\Users\USER\Desktop\Programs\adaptive-mlops\frontend> npm run build
vite v8.3.3 building client environment for production...
✓ 81 modules transformed.
dist/index.html                   0.45 kB │ gzip:  0.29 kB
dist/assets/index-p8pEZ9iB.css    2.47 kB │ gzip:  1.02 kB
dist/assets/index-D75v4FMP.js   316.46 kB │ gzip: 97.27 kB
✓ built in 272ms
Exit Code: 0
```

---

## 8. Live Integration & Browser E2E Verification

### Live Container Integration Test
```
PS C:\Users\USER\Desktop\Programs\adaptive-mlops> python scripts/ci/integration_tests.py
Running API Integration Tests against: http://localhost:8000...
Integration test passed against running service: label='billing', confidence=0.3711031610096057
Exit Code: 0
```

### Headless Chrome Selenium E2E Test
```
PS C:\Users\USER\Desktop\Programs\adaptive-mlops> python scripts/ci/selenium_tests.py
Starting Selenium E2E Browser Test against: http://localhost:5173...
Navigating to frontend...
Page Title: frontend
Root DOM node verified.
DOM text sample: Login to AdaptiveMLOps
Selenium E2E Test passed successfully against real browser instance.
Exit Code: 0
```
