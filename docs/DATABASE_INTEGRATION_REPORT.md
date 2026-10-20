# AdaptiveMLOps — InsForge Database Integration Report

**Date:** October 20, 2026  
**Status:** CONNECTED & FULLY VERIFIED (100%)  
**Target Database:** InsForge Managed PostgreSQL 15  
**Auditor:** Automated Engineering Remediation Team  

---

## 1. Executive Summary

The **AdaptiveMLOps** platform has been successfully integrated with the remote **InsForge PostgreSQL** cloud database service. Real connectivity, complete schema reconciliation, transactional data persistence, and environment separation have been independently tested and verified.

Key accomplishments:
1. **Remote Connectivity:** Direct TLS/SSL-encrypted connectivity established to `bdrb7j6b.ap-southeast.database.insforge.app:5432/insforge`.
2. **Schema Reconciliation:** Inspected all 14 tables, columns, indexes, and foreign keys on the remote InsForge database. The remote database matches the SQLAlchemy models and Alembic revision `d87536722e30` with zero schema drift.
3. **Data Preservation:** Existing records (including pre-existing datasets, model versions, predictions, and retraining jobs) were strictly preserved. No destructive migrations (`DROP`, `TRUNCATE`, or overwrite) were executed.
4. **Environment Isolation:** Hardened test execution in `backend/tests/conftest.py` so that automated test suites (`pytest`) run exclusively against an isolated test engine (`sqlite+aiosqlite:///:memory:`), completely protecting the remote InsForge database from accidental table drops or test data contamination.
5. **Real Persistence Verified:** Verified that live predictions, linked feedback records, model deployments, health checks, approvals, and audit logs persist with complete relational constraint integrity.
6. **Credential Security:** All hardcoded credentials have been removed from source files and patch scripts. Sensitive credentials are read from `.env` and environment variables. `.env` is confirmed excluded from git tracking.

---

## 2. InsForge Project Configuration

| Setting | Configuration Value | Effective Source |
| :--- | :--- | :--- |
| **Project URL** | `https://bdrb7j6b.ap-southeast.insforge.app` | `INSFORGE_PROJECT_URL` |
| **Host** | `bdrb7j6b.ap-southeast.database.insforge.app` | `POSTGRES_HOST` / `DATABASE_HOST` |
| **Port** | `5432` | `POSTGRES_PORT` / `DATABASE_PORT` |
| **Database** | `insforge` | `POSTGRES_DB` / `DATABASE_NAME` |
| **Username** | `postgres` | `POSTGRES_USER` / `DATABASE_USER` |
| **Password** | Configured securely in `.env` | `POSTGRES_PASSWORD` / `DATABASE_PASSWORD` |
| **SSL Mode** | `require` (TLS connection) | `DATABASE_SSL_MODE` / `POSTGRES_SSLMODE` |
| **API Key** | Configured securely in `.env` | `INSFORGE_API_KEY` |
| **Anon Key** | Configured securely in `.env` | `INSFORGE_ANON_KEY` |

> [!NOTE]
> **Password URL-Encoding:** The database configuration in `backend/app/config.py` uses `urllib.parse.quote_plus` when assembling connection strings from individual environment variables, ensuring passwords with special characters are safely encoded.

---

## 3. Environment Separation Architecture

To prevent accidental data loss or coupling across deployment stages, the platform separates environments:

```
[ Automated CI / Pytest ] ──> Isolated SQLite In-Memory Engine (conftest.py)
[ Local Development ]     ──> Docker PostgreSQL 15 Container (localhost:5432)
[ Staging / Production ]   ──> Remote InsForge PostgreSQL Cloud Instance (SSL Require)
```

1. **Automated Testing:** `backend/tests/conftest.py` configures a dedicated `test_engine` (`sqlite+aiosqlite:///:memory:`) and overrides session factories and dependency providers. Automated test runs never connect to or drop tables on the remote InsForge database.
2. **Local Development:** Default fallback points to the local containerized PostgreSQL service (`postgresql+psycopg2://postgres:postgres@localhost:5432/adaptive_mlops`).
3. **Remote Integration / Production:** When `POSTGRES_HOST=bdrb7j6b.ap-southeast.database.insforge.app` and credentials are provided in `.env`, the FastAPI application connects seamlessly via asyncpg and psycopg2 using TLS encryption (`sslmode=require`).

---

## 4. Connectivity and Readiness Verification

Direct read-only probes were executed to verify remote database connectivity:

```
Command: python scratch/test_insforge_conn.py
Result:
  - Connectivity check (SELECT 1): True
  - Current Database: insforge
  - PostgreSQL Version: PostgreSQL 15.18 (Debian 15.18-1.pgdg13+1) on aarch64-unknown-linux-gnu
  - Existing public tables (14): alembic_version, approvals, audit_logs, datasets, deployments, 
    drift_runs, evaluation_runs, feedback, health_checks, model_audits, model_versions, 
    predictions, retraining_jobs, training_runs
  - Alembic version in remote DB: ['d87536722e30']
Exit Code: 0
```

Both synchronous (`psycopg2`) and asynchronous (`asyncpg`) database drivers verified clean handshakes over port 5432 with SSL enabled.

---

## 5. Real Data Persistence Verification

An end-to-end transactional lifecycle test was executed against the live InsForge PostgreSQL database using safe, tagged test records:

1. **Existing Baseline Model Discovery:** Successfully resolved active champion model `v1.0.0` (`id=9e497ca5-df85-4cb4-ad6c-6ee646171525`).
2. **Prediction Persistence:** Created and committed a real `Prediction` record (`id=45105834-a2af-4bc8-bf42-5c632212aaa4`, text="InsForge live persistence verification test", label="billing", confidence=0.985).
3. **Linked Feedback Persistence:** Created and committed a real `Feedback` record (`id=ddf826be-8c84-4849-befe-a717add01182`) with foreign key constraint referencing the prediction ID.
4. **Relational Query Verification:** Queried both records back from InsForge; verified text integrity, predicted label, confidence, and foreign key reference.
5. **Governance & Audit Logging:** Persisted a `Deployment` record (`SUCCESS`), a linked `HealthCheck` record (`is_healthy=True`), an `Approval` record (`status=APPROVED`), and an `AuditLog` record (`action=DEPLOYMENT_SUCCEEDED`).
6. **Constraint Verification:** All foreign keys (`feedback.prediction_id -> predictions.id`, `health_checks.deployment_id -> deployments.id`, `deployments.model_version_id -> model_versions.id`) verified valid and enforced.
7. **Clean Teardown:** Selectively deleted only the test records created during the test run.
8. **State Preservation Confirmation:** Verified that all pre-existing production records (8 predictions, 5 model versions, 4 datasets) remained intact.

---

## 6. Frontend and Backend Integration

1. **Frontend Architecture:** The React + TypeScript frontend connects exclusively to backend REST API endpoints (`/api/v1/...`). No database connection strings, passwords, or direct PostgreSQL client libraries exist in the frontend codebase.
2. **Service Layer Integrity:** Backend endpoints (`predictions.py`, `feedback.py`, `registry.py`, `retraining.py`, `governance.py`) use FastAPI dependency injection (`get_db`) with SQLAlchemy `AsyncSession` providing transaction demarcation (`commit()` on success, `rollback()` on exceptions).
3. **Health & Readiness Endpoints:**
   - `/api/v1/health`: Pure liveness check returning HTTP 200 `{"status": "ok"}`.
   - `/api/v1/ready`: Dependency readiness check executing `SELECT 1` against the InsForge database and checking model readiness in `prediction_service`.

---

## 7. Configuration Sanitization and Remaining Limitations

### Sanitized Files
- `backend/app/config.py`: Dynamic URI generation from environment variables; zero hardcoded secrets.
- `backend/patch_config.py` & `backend/patch_env.py`: Sanitized to read from environment variables.
- `.env.example` & `backend/.env.example`: Updated with clean placeholder templates.
- `.gitignore`: Validated to exclude `.env`, `.env.*` (except `.env.example`).

### Remaining Limitations
1. **Network Latency:** Connecting to an `ap-southeast` cloud PostgreSQL database from external networks introduces ~80–150ms round-trip latency compared to local Docker container databases. Connection pooling (`pool_pre_ping=True`) is enabled to minimize handshake overhead.
2. **Demo Mode Gating:** Demonstration endpoints (`/demo/*`) are enabled when `ENABLE_DEMO_MODE=true`. In non-demo production environments, ensure `ENABLE_DEMO_MODE=false`.
