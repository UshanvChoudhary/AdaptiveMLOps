# AdaptiveMLOps — Autonomous Continuous ML Lifecycle Platform

AdaptiveMLOps is an end-to-end Machine Learning Operations (MLOps) platform demonstrating continuous retraining, feedback loops, server-side quality gates, role-based governance, and automated deployment/rollback capabilities.

---

## 1. System Architecture

```
[ Frontend: React + TypeScript + Vite ]
                   │
                   ▼  (REST API with JWT / X-API-Key)
[ Backend: FastAPI (Python 3.10+) ]
       │              │               │
       ▼              ▼               ▼
[ PostgreSQL 15 ] [ Disk Registry ] [ In-Memory Prediction Service ]
(Alembic Migrations)  (ml/artifacts/)   (TF-IDF + Logistic Regression)
```

- **Backend API:** FastAPI with SQLAlchemy, Alembic, and Pydantic v2.
- **Database:** PostgreSQL 15 with 14 relational tables supporting full auditable lifecycle state transitions.
- **Frontend Dashboard:** React 18, TypeScript, and Vite with tabbed interfaces for Predictions, Feedback, Retraining, Registry, Governance, Monitoring, and Demo controls.
- **Machine Learning Core:** Customer Support NLP Intent Classifier utilizing scikit-learn's `TfidfVectorizer` paired with multi-class `LogisticRegression` (`billing`, `technical_support`, `refund`, `account_management`).
- **CI/CD Automation:** Jenkins declarative pipeline running linting, unit tests, data validation, candidate training, quality gates, Docker container builds, live integration testing, and headless Chrome Selenium E2E tests.

---

## 2. Machine Learning Lifecycle

1. **Inference & Prediction Logging:** Users submit text queries to `/api/v1/predictions/predict`. The active production model returns predicted intent, class probabilities, confidence score, and latency.
2. **Ground Truth Feedback:** Real-world outcomes and human corrections are posted to `/api/v1/feedback`. Feedback records accumulate with status `NEW`.
3. **Automated Retraining:** When feedback reaches threshold or upon admin trigger (`/api/v1/retraining/trigger`), the engine:
   - Aggregates base training samples with pending user feedback.
   - Computes a cryptographic SHA-256 dataset checksum.
   - Fits the vectorizer and classifier pipeline.
   - Evaluates real metrics (`accuracy`, `macro F1`, `p95 latency`) on held-out splits.
   - Serializes real versioned artifacts (`model.joblib`, `vectorizer.joblib`, `metadata.json`) into `ml/artifacts/{candidate_version}/`.
   - Transitions feedback records from `NEW` to `USED_IN_TRAINING`.
4. **Server-Side Quality Gates:** Candidate models cannot be promoted unless they satisfy configured quality gates:
   - Validation F1 $\ge 0.80$
   - Validation Accuracy $\ge 0.80$
   - p95 Inference Latency $\le 100.0$ ms
   - Valid candidate artifact present on disk
5. **Promotion & Hot Reloading:** Upon admin promotion (`/api/v1/registry/models/{id}/promote`), the candidate becomes `PRODUCTION`, the prior champion is `ARCHIVED`, and the in-memory prediction service immediately reloads the new artifact with zero downtime.
6. **Rollback:** In the event of an issue, rollback (`/api/v1/governance/rollback`) verifies the previous artifact on disk, hot-reloads it into memory, registers a new deployment, and restores the previous production model.

---

## 3. Security, Authentication, and RBAC

- **Authentication Methods:**
  - **JWT Bearer Tokens:** OAuth2 password flow (`/api/v1/auth/token`).
  - **API Keys:** Administrative service access via `X-API-Key` header.
- **Role-Based Access Control (RBAC):**
  - `ADMIN`: Model promotion, deployments, rollbacks, retraining triggers.
  - `REVIEWER`: Model candidate approval and rejection.
  - `USER`: Inference requests and feedback submission.
- **Local Demo Mode Guard:**
  - Controlled by the environment variable `ENABLE_DEMO_MODE=true` (or `false`).
  - When disabled (`false`), demo user accounts (`admin`, `reviewer`, `user`) are rejected with `HTTP 401 Unauthorized`, and all `/demo/*` mutation endpoints return `HTTP 403 Forbidden`.
- **Credential Rotation Notice:**
  - Any historical credentials discovered in previous versions (including external database connection strings and default JWT secrets) must be rotated immediately in all environments. Never deploy default `.env.example` secrets to staging or production.

---

## 4. Health and Readiness Probes

The service implements standard cloud-native Kubernetes/container health probes:
- **Liveness Probe (`GET /api/v1/health`):** Lightweight check returning `{"status": "ok"}` indicating the process is responsive.
- **Readiness Probe (`GET /api/v1/ready`):** Deep dependency check verifying that PostgreSQL database is reachable (`SELECT 1`) and the ML prediction model is loaded in memory. Returns HTTP 200 `{"status": "ready", "database": "connected", "model": "loaded"}` or HTTP 503 if unavailable.

---

## 5. Local Setup and Quickstart

### Prerequisites
- Docker Engine & Docker Compose
- Python 3.10+
- Node.js 20+

### Running via Docker Compose
```bash
# 1. Clone repository
git clone <repo-url>
cd adaptive-mlops

# 2. Configure environment
cp .env.example .env

# 3. Start services
docker-compose up --build
```
- Frontend UI: `http://localhost:5173` (or `http://localhost:3000`)
- Backend API Docs: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/v1/ready`

### Running Tests Locally

#### Backend Tests (Unit, RBAC, ML, and 10 Negative Scenarios)
```bash
python -m pytest backend/tests -v
```

#### Frontend Linting & Build
```bash
cd frontend
npm run lint
npm run build
```

#### Database Migrations (from empty PostgreSQL)
```bash
cd backend
alembic upgrade head
```

#### CI Integration & Selenium Tests
```bash
python scripts/ci/integration_tests.py
python scripts/ci/selenium_tests.py
```

---

## 6. Honest Limitations

1. **Local Filesystem Model Storage:** Candidate artifacts are saved to `ml/artifacts/` on the local filesystem. For horizontal multi-node scaling, an object store (e.g. S3, GCS, or MinIO) should be mounted.
2. **Synchronous In-Process Retraining:** Retraining currently executes via FastAPI background tasks within the API container. In large-scale enterprise deployments, model training should be dispatched to an asynchronous distributed task runner (e.g. Celery or Kubeflow).
3. **Simulated Drift Event Generation:** The `/demo/simulate-drift` endpoint synthesizes drift distribution entries for demonstration purposes. True production drift monitoring requires continuous streaming distribution calculations across large batches of live production inputs.
