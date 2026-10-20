# AdaptiveMLOps - Final Demo Guide (Professor Demonstration)

This guide provides a reliable, deterministic 7-10 minute demonstration sequence for the entire MLOps lifecycle using the "Demo Mode" controls. 

## Preparation
1. Ensure the system is running (`docker-compose up` or via local servers).
2. Open the UI and log in using demo credentials (`admin` / `password`).
3. Navigate to the **Demo Controls** tab (highlighted in red with a "⚠️ PROFESSOR DEMO MODE ⚠️" warning).

## Step-by-Step Sequence

### 1. Initial State (1 min)
- **Action**: Click `Seed Data`.
- **Expected Result**: A success message appears. The database is now seeded with initial users, a baseline champion model (`xgboost v1.0`), and initial audit events.
- **Narrative**: "We start with a baseline model already deployed. The system is currently running in a stable state."

### 2. Predictions & Feedback (1.5 min)
- **Action**: Click `1. Generate Feedback`.
- **Expected Result**: The system generates a deterministic prediction log and corresponding user feedback.
- **UI Check**: Navigate to **Predictions & Feedback** tab to show the prediction and actual values aligning.
- **Narrative**: "Users are interacting with our model. The system captures the inputs, predictions, and the actual outcomes (feedback) to measure real-world performance."

### 3. Monitoring & Drift (1 min)
- **Action**: Click `8. Simulate Drift`.
- **Expected Result**: A drift event is recorded for `demo_feature`.
- **UI Check**: Navigate to **Monitoring & Drift** tab to show the drift alert.
- **Narrative**: "The environment changes over time. Our monitoring detects a statistical drift in a key feature, alerting us that the model's assumptions may be outdated."

### 4. Triggering Retraining (1 min)
- **Action**: Click `2. Trigger Retraining`.
- **Expected Result**: A retraining job is queued and executed by the backend.
- **UI Check**: Navigate to **Retraining Engine** tab. You should see a pending/completed job.
- **Narrative**: "In response to drift and accumulated feedback, we trigger our automated retraining pipeline to build a new model."

### 5. Candidate Evaluation (1 min)
- **Action**: Click `3a. Create Good Challenger` (or `3b` for a bad one).
- **Expected Result**: A new model version (`v1.1-good`) is registered with higher metrics (e.g., 95% accuracy).
- **UI Check**: Navigate to **Model Registry** tab to see the new model in the registry but not active.
- **Narrative**: "The pipeline produced a new candidate model. We compare its validation metrics against our current champion."

### 6. Quality Gate & Promotion (1.5 min)
- **Action**: Click `4. Run Quality Gate`, then `5. Promote Model`.
- **Expected Result**: Audit logs record the successful quality gate check and the promotion of the challenger.
- **UI Check**: Navigate to **Model Promotion** tab to show the status.
- **Narrative**: "The candidate model must pass strict automated quality gates. Once it passes, an admin can approve its promotion."

### 7. Deployment Failure & Rollback (1.5 min)
- **Action**: Click `6. Simulate Deploy Fail`. Then click `7. Rollback`.
- **Expected Result**: Deployment fails (simulated), triggering a rollback to `v1.0`. 
- **UI Check**: Navigate to **Governance** tab to show the failed deployment and subsequent rollback in the audit logs.
- **Narrative**: "Even if a model passes tests, deployment to production can fail (e.g., infrastructure issues, health check timeouts). Our system detects this immediately and automatically rolls back to the last known good state, ensuring zero downtime."

### 8. System Lifecycle (0.5 min)
- **Action**: Navigate to the **Lifecycle** tab.
- **Narrative**: "This summarizes the complete lifecycle we just traversed: from predictions to feedback, retraining, evaluation, quality gating, deployment, and finally, automated rollback capabilities."

## Conclusion
This demo mode provides a fully robust end-to-end trace of a mature MLOps architecture without the unreliability of stochastic training or external API dependencies. Every event is audited, and the separation of concerns (Reviewer vs Admin) is strictly maintained.
