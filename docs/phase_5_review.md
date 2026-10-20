# Phase 5 Review: Identified Issues

Upon reviewing the Phase 5 implementation against the PRD requirements and best practices, I've identified the following issues:

## 1. Architectural & Traceability Issues
*   **Missing Feedback-to-Dataset Traceability:** We create a Dataset snapshot (mocked) and set the feedback's eedback_status to "processed", but there is no linkage between the Feedback rows and the Dataset. To ensure complete model lineage (as required in Phase 4), we must know exactly which feedback items comprised a specific dataset.
    *   **Fix:** Add a dataset_id foreign key to the Feedback table, or a mapping table. Since a feedback item is typically consumed by one retraining iteration to form a new dataset baseline, adding dataset_id to Feedback is the simplest way to link them.

## 2. Database & Concurrency Issues
*   **Race Conditions in Triggering:** The 	rigger_retraining function checks for an existing job (existing = db.query(RetrainingJob)...first()), but doesn't lock the table. If two requests hit the endpoint simultaneously, they could both trigger a retraining job, violating the rule.
    *   **Fix:** We could use a unique constraint or a locking mechanism, though in SQLite with_for_update behavior varies. Given it's a lightweight project, relying on the QUEUED / RUNNING status check is mostly okay, but we should make sure we process feedbacks safely.
*   **Pagination Missing:** The /api/v1/retraining/jobs endpoint returns .all() jobs. This will not scale.
    *   **Fix:** Implement standard skip and limit pagination.

## 3. Testing Issues
*   **Mock Training Hardcodes:** The un_retraining_job hardcodes metrics (ccuracy: 0.85, f1_score: 0.84). While a placeholder is expected, we should at least simulate variation or ensure it reads mock training results logically to test threshold/degradation logic later.
*   **Missing Tests:** There are no tests for edge cases, such as when there is no eligible feedback (which should fail gracefully), or pagination limits.

## 4. API & Security Issues
*   **Unbounded Query:** db.query(Feedback).filter(...).all() could load millions of rows into memory during dataset snapshotting.
    *   **Fix:** It should stream the data, or we just process them in batches, or we just take the first N (e.g. limit to 10000).

Let me know if you would like me to implement these fixes!
