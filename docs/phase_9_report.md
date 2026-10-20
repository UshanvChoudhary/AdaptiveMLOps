# Phase 9: Intelligent Monitoring and Drift Detection

## Objective
Add intelligent monitoring and drift detection to track application health, model performance, and data distribution shifts over time.

## Work Completed

### 1. Database Schema
- Added `drift_runs` table (`DriftRun` model) to store historical drift analysis results.
- Recorded fields: `drift_score`, `status`, `reference_dataset_id`, `current_window_start`, `current_window_end`, `class_distribution`, `confidence_trend`, `input_distribution`, `recommended_action`, `created_at`.
- Registered the model in `backend/migrations/env.py` and created/applied a new Alembic migration.

### 2. Drift Analysis Logic
- Implemented `drift_service.py` with `calculate_drift` logic that analyzes predictions within a moving window.
- **Analyzed Distributions**:
  - **Input Distribution**: Tracking average input text length.
  - **Class Distribution**: Detecting major imbalances in recent predicted labels.
  - **Confidence Distribution**: Monitoring the mean confidence score of recent predictions.
- **Drift Scoring**: Calculates a composite drift score based on confidence degradation and class imbalance.
- **Configurable Thresholds**:
  - `DRIFT_THRESHOLD_WARNING = 0.3`
  - `DRIFT_THRESHOLD_CRITICAL = 0.5`
- **Recommended Actions**: Emits status (`NORMAL`, `WARNING`, `CRITICAL`) and actionable recommendations (e.g., "Trigger Retraining Pipeline immediately.") based on severity. It intentionally does NOT auto-deploy a new model, adhering strictly to the constraints.

### 3. API Endpoints
- **Drift Routes (`/api/v1/drift`)**:
  - `POST /api/v1/drift/run`: Executes on-demand drift analysis and returns the resulting report.
  - `GET /api/v1/drift/latest`: Retrieves the most recent drift report.
- **Metrics Routes (`/api/v1/metrics`)**:
  - `GET /api/v1/metrics`: Computes overall application metrics over a rolling window.
  - Returns `prediction_count`, `p95_latency`, `error_rate`, `feedback_correction_rate`, `model_f1`, and `drift_score`.

### 4. Frontend Dashboards
- **MonitoringDashboard.tsx**: A high-level overview of application metrics (Total Predictions, Error Rate, P95 Latency, Feedback Rate).
- **DriftDashboard.tsx**: A specialized dashboard that visualizes the latest drift metrics, score, status, and distributions (Confidence Trend, Class Imbalance, Text Lengths).
- **Navigation Integration**: Added Monitoring and Drift tabs into the `App.tsx` main navigation layout.

## Verification
- End-to-End API verification completed successfully.
- Predictions were accurately logged, metrics correctly aggregated, and drift detection logically identified `CRITICAL` state shifts when confidence dropped.
- Adhered to the constraint of avoiding over-engineering by using practical statistical distribution methods tailored for a student MLOps project.
- Verified that Jenkins integration is strictly separated from ML business logic.

### 5. Architectural & Security Review (Post-Implementation)
- **CI Test Client Stability**: Addressed an architectural issue where `TestClient` was being instantiated globally in CI scripts (`scripts/ci/*.py`), leading to database session and lifespan-related non-deterministic failures. It is now correctly mapped as a context manager (`with TestClient(app) as client:`).
- **Schema Migrations**: Fixed `alembic` migrations specifically for SQLite compatibility during local development. SQLite's limitations with complex `ALTER` statements required the usage of `batch_alter_table` explicitly.
- **Resource Exhaustion**: Modified aggregation queries in `metrics.py` and `drift_service.py` to prevent "Out-of-Memory" (OOM) risks. Query processing was moved from loading whole records into Python memory towards using database-native functions (`func.count`, `.limit()`, etc.).
- **Security & CORS**: Standardized dynamic CORS generation in `config.py` based on `BACKEND_CORS_ORIGINS` to prevent wildcard exposure.

## Next Steps
Proceed to Phase 10 (Advanced Analytics & Reporting) or finalize project delivery.
