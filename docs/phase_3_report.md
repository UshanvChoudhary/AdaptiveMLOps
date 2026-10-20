# AdaptiveMLOps - Phase 3 Report

## Objective
Create the first complete user workflow, integrating the React frontend with the FastAPI ML backend, implementing user inference tracking and feedback persistence logic.

## Implementation Details

1. **Database Modeling:**
   - Designed and built the Feedback SQLAlchemy model mapping explicitly to the generated prediction inferences via a one-to-one foreign key (prediction_id).
   - Recorded is_correct, corrected_label, comments, and timestamps to persist human-in-the-loop insights.
   - Designed a new Alembic migration encapsulating these changes for seamless deployment.

2. **Backend Feedback API:**
   - Endpoint: POST /api/v1/predictions/{prediction_id}/feedback.
   - Hardened FeedbackRequest Pydantic models to assert critical business rules dynamically. If is_correct equals alse, the validator guarantees corrected_label is included.
   - Enforced database IntegrityError constraints on duplicates: returning 409 Conflict gracefully if feedback is sent multiple times for the same prediction.
   - Endpoint: GET /api/v1/feedback/me for reviewing historical user inputs.

3. **Frontend Application:**
   - Extended the Vite+React application (rontend/src/App.tsx) to orchestrate a seamless interface.
   - The user inputs text, clicks 'Get Prediction' which asynchronously communicates with the API POST /api/v1/predictions/.
   - The result explicitly surfaces the Model Version and Confidence interval to the UI per the PRD requirements.
   - Presents "Correct / Incorrect" feedback prompts dynamically.
   - Selecting 'Incorrect' presents a dropdown with valid category corrections, successfully pushing corrected_label back to the backend payload.

4. **Testing Suite:**
   - Expanded unit and integration Pytest suites with 	ests/test_feedback.py covering positive paths, Pydantic failure blocks, and DB duplicate 409 collisions.
   - Scaffolded an initial Selenium E2E automated test 	ests/test_e2e.py configured with Headless Chrome. It formally navigates the frontend application, executes text inference, reads elements, selects the correction dropdown, and successfully validates the success message.

## Status
**Phase 3 Complete.** End-to-end integration mapping frontend interactions directly into the backend intelligence persistence layer is fully functional.

**Post-Implementation Fixes (Completed):**
- Resolved dynamic API routing on the frontend by properly injecting "VITE_API_URL" environment variables.
- Hardened label validation using runtime dynamic loading from the ML model directly into the validation layer.
- Fixed Selenium End-to-End tests failing due to SQLite DateTime serialization inconsistencies ("func.now()" vs "CURRENT_TIMESTAMP"). Both backend models and alembic migrations successfully adapted to ensure SQLite compatibility during local E2E test environments.
- Relocated and consolidated E2E tests into a standalone "tests/e2e/test_feedback_flow.py" for decoupled infrastructure execution.
